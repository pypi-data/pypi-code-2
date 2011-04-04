"""
MachineLearning.py
Perform Machine Learning algorithms on Feature Matrices.
@project: pharmaduke
@author: Nicholas P. Tatonetti & Guy Haskin Fernald
"""

import math
import numpy
import tempfile
import operator
import subprocess
import namedmatrix as nm

from StringIO import StringIO
from pylab import *
from copy import copy, deepcopy
import random

WEKA_CLASSPATH = "/Applications/weka-3-6-1.app/Contents/Resources/Java/weka.jar"

class ImplementationMissing(Exception):
    pass


class FeatureSelection(object):
    """
    A general class to perform feature selection of the 
    example data.
    """
    
    def __init__(self, examples, labels, mlclass, max_features=None):
        """
        @param: examples    NamedMatrix of feature vectors, each row is a training example.
        @param: labels      Classification labels, a list of integer or boolean values.
        @param: mlclass     A MachineLearning subclass.
        """
        
        self.examples = examples
        self.labels = labels
        self.mlclass = mlclass
        if type(max_features) == int:
            self.max_features = max_features
        elif type(max_features) == float:
            self.max_features = int(max_features * self.examples.size(0))
        elif max_features is None:
            self.max_features = self.examples.size(1)
        
        self.folds = None
        
    
    def divide_examples(self, num_folds):
        """
        Divide the training examples into num_folds.
        """
        rows = self.examples.rownames
        folds_names = dict()
        folds_index = dict()
        
        for i,row in enumerate(rows):
            rand_fold = random.randint(0,num_folds-1)
            
            if not rand_fold in folds_names:
                folds_names[rand_fold] = list()
            if not rand_fold in folds_index:
                folds_index[rand_fold] = list()
            
            folds_names[rand_fold].append(row)
            folds_index[rand_fold].append(i)
        
        self.folds = dict()
        self.folds['names'] = folds_names
        self.folds['index'] = folds_index
    
    def forward_selection(self, num_folds=5, statistical_test="wilcox.test", args = None):
        """
        Perform forward selection and return a mlclass classifier trained
        with those features.
        @param: folds               The number-fold cross-validation to perform.
        @param: statistica_test     The type of statistical test to perform. Requires rpy2 and R to be installed.
        """
        import rpy2.robjects as robjects
        
        self.divide_examples(num_folds)
        feature_sets = list()
        for i in range(num_folds):
            
            train_rows = reduce(operator.add, [fold for k,fold in self.folds['names'].items() if not k == i])
            train_data = self.examples[train_rows,:]
            train_index = reduce(operator.add, [fold for k,fold in self.folds['index'].items() if not k == i])
            train_labels = [self.labels[k] for k in train_index]
            
            test_rows = reduce(operator.add, [fold for k,fold in self.folds['names'].items() if k == i])
            test_index = reduce(operator.add, [fold for k,fold in self.folds['index'].items() if k == i])
            test_data = self.examples[test_rows,:]
            test_labels = [self.labels[k] for k in test_index]
            
            pvalues = list()
            for j,feat in enumerate(self.examples.colnames):
                
                if statistical_test == "wilcox.test":
                    positive_values = ",".join(map(str,[train_data[k,j] for k in range(train_data.size(0)) if train_labels[k] == 1]))
                    negative_values = ",".join(map(str,[train_data[k,j] for k in range(train_data.size(0)) if train_labels[k] == 0]))
                    pvalue = robjects.r("wilcox.test(c(%s), c(%s))$p.value" % (positive_values, negative_values))[0]
                
                pvalues.append( (pvalue,feat,j) )
            
            selected = [feat for p,feat,j in sorted(pvalues) if p < 0.05][:self.max_features]
            
            best_features = None
            print >> sys.stderr, "Fold %d: Found %d enriched features." % (i, len(selected))
            for k in range(len(selected)):
                
                train = train_data[:,selected[:k]]
                test = test_data[:,selected[:k]]
                
                mlobj = self.mlclass(train, train_labels)
                train_results = mlobj.cross_validate()
                test_results = mlobj.test(test, test_labels)
                
                print >> sys.stderr, "  %d    %f  %f  %f" % (k, train_results['AUROC'], train_results['TrainingError'], test_results['TestError'])
                
                if best_features is None or test_results['TestError'] < best_features[0]:
                    best_features = (test_results['TestError'], test_results['TrainingError'], selected[:k])
            
            feature_sets.append( best_features )
        
        best_feature_set = sorted(feature_sets)[0]
        return {'SelectedFeatures':best_feature_set[2], 'TestError':best_feature_set[0], 'TrainingError':best_feature_set[1]}

class MachineLearning(object):
    """
    A abstract Machine Learning object. A ML object is not instantiated
    directly, but a subclass (eg. NaiveBayes, Logistic, SVM) is. The
    following defines how to use this children of ML objects.
    
    Initilization:
    ==============
    The machine learning object is initialized with a example matrix
    and a list of labels. The example matrix is expected to be a 
    NamedMatrix and the label list is a list of integers or boolean
    values.
    
    Methods:
    =================
    train:
    Train the model on the example.
    
    predict:
    Predict classifications for the input examples.
    
    cross_validate:
    Perform a cross-validation of the classifier.
    """
    
    def __init__(self, examples, labels):
        """
        Initialize the MachineLearning object.
        @param: examples    NamedMatrix of feature vectors, each row
                            is a training example.
        @param: labels      Classification labels, a list of integer
                            or boolean values.
        """
        super(MachineLearning, self).__init__()
        self.examples = examples
        self.labels = numpy.matrix(labels).transpose()
    
    def train(self):
        raise ImplementationMissing("abstract train method must be implemented by subclass")
    
    def predict(self, examples):
        raise ImplementationMissing("abstract predict method must be implemented by subclass")
    
    def cross_validate(self):
        raise ImplementationMissing("abstract cross_validate method must be implemented by subclass")

WEKA_ARGS = ["java", "-Xmx4096m", "-classpath", WEKA_CLASSPATH]

class WekaML(MachineLearning):
    """
    WekaML is an abstact MachineLearning class that wraps the weka machine learning tools.
    WekaML can be subclassed for specific machine learning methods (eg NaiveBayes class)
    or can be used directly by setting the weka_method attribute. Any extra params that
    you want to pass to classifier can be set using the classifier_params attribute.
    
    The following two instantiations are equivalent:
    ====
    nb = WekaML(X, y)
    nb.weka_method = 'weka.classifiers.bayes.NaiveBayes'
    nb.classifier_params = ['-K']
    ====
    nb = NaiveBayes(X, y)
    ====
    """
    def __init__(self, obj, labels = None):
        super(WekaML, self).__init__(obj, labels)
        self.weka_method = None
        self.classifier_params = []
        self._generate_arff_data()
    
    @staticmethod
    def named_to_arff(examples):
        """
        Convert the NamedMatrix examples to arff (weka) data format.
        Do so without loading up weka.
        """
        csvio = StringIO()
        label_transform = lambda X: [x if i < len(X)-1 else 'yes' if bool(x) else 'no' for i,x in enumerate(X)]
        examples.save_to_file(csvio, row_labels=False, column_labels=False, transform=label_transform)
        csv_data = csvio.getvalue()
        
        arff_data = "@relation named_to_arff\n\n"
        for column in examples.colnames[:-1]:
            arff_data += "@attribute %s numeric\n" % column
        arff_data += '@attribute class {yes,no}\n\n'
        arff_data += '@data\n'
        arff_data += csv_data
        return arff_data
    
    @staticmethod
    def process_threshold_file(temp_threshold_file):
        """
        Read data from threshold file and return a dictionary of values:
        Keys:
        AUROC   The Area under the Receiver Operating Characteristic Curve
        AUPR    The Aera under the Precision-Recall Curve.
        TPR     A list of True Positive Rates
        FPR     A list of False Positive Rates
        PR      A list of Precisions
        RE      A list of Recalls.
        """
        roc_data = subprocess.Popen(["cat",temp_threshold_file], stdout=subprocess.PIPE).communicate()[0]
        
        FPRs = list()
        TPRs = list()
        PRs = list()
        REs = list()
        auroc = 0.0
        aupr = 0.0
        
        for i,line in enumerate(roc_data.split('@data')[1].split('\n')[1:] + ["0,0,0,0,0,0,1,0,0,0,0"]):
            TP,FN,FP,TN,FPR,TPR,PR,RE,fallout,fmeasure,threshold = map(float,line.split(','))
            if i > 0:
                auroc += (FPRs[-1]-FPR)*(TPR)+0.5*(FPRs[-1]-FPR)*(TPRs[-1]-TPR)
                aupr += (REs[-1]-RE)*(PR)+0.5*(REs[-1]-RE)*(PRs[-1]-PR)
            FPRs.append(FPR)
            TPRs.append(TPR)
            PRs.append(PR)
            REs.append(RE)
        
        return {'AUROC':auroc, 'AUPR':aupr, 'TPR':TPRs, 'FPR':FPRs, 'PR':PRs, 'RE':REs }
    
    def _generate_arff_data(self):
        training_data = nm.NamedMatrix(None, self.examples.rownames, self.examples.colnames + ["class"])
        training_data[:,:self.examples.size(1)] = self.examples
        training_data[:,-1] = self.labels
        
        self.arff_data = WekaML.named_to_arff(training_data)
    
    def test(self, test_examples, test_labels):
        """
        Train a model on the training data and then test on the test_examples.
        """
        # Convert the test_examples and labels to arff data.
        test_data = nm.NamedMatrix(None, test_examples.rownames, test_examples.colnames + ["class"])
        test_data[:,:test_examples.size(1)] = test_examples
        test_data[:,-1] = numpy.matrix(test_labels).transpose()
        test_arff = WekaML.named_to_arff(test_data)
        
        temp_training_arff = tempfile.mkstemp(suffix=".arff")[1]
        tmpfh = open(temp_training_arff, 'w')
        tmpfh.write(self.arff_data)
        tmpfh.close()
        
        temp_testing_arff = tempfile.mkstemp(suffix=".arff")[1]
        tmpfh = open(temp_testing_arff, 'w')
        tmpfh.write(test_arff)
        tmpfh.close()
        
        temp_threshold_file = tempfile.mkstemp(suffix=".arff")[1]
        weka_output = subprocess.Popen(WEKA_ARGS + \
            [self.weka_method, \
            "-t", temp_training_arff, \
            "-T", temp_testing_arff, \
            "-threshold-file", temp_threshold_file, \
            "-threshold-label", "yes"] + self.classifier_params, \
            stdout=subprocess.PIPE).communicate()[0]
        
        train_error = None
        test_error = None
        try:
            train_error = float(weka_output.split('=== Error on training data ===')[1].split('\n')[5].split()[-1])
            test_error  = float(weka_output.split('=== Error on test data ===')[1].split('\n')[5].split()[-1])
        except IndexError:
            print >> sys.stderr, "Failed to get training and test error out of output"
        
        thresh_results = WekaML.process_threshold_file(temp_threshold_file)
        TPRs = thresh_results['TPR']
        FPRs = thresh_results['FPR']
        PRs = thresh_results['PR']
        REs = thresh_results['RE']
        self.weka_output = weka_output
        self.plot_data = (TPRs, FPRs, PRs, REs)
        
        return {"TrainingError":train_error, "TestError":test_error, "AUROC":thresh_results['AUROC'], "AUPR":thresh_results['AUPR']}
    
    # def predict(self, test_examples, test_labels):
    #     """
    #     Use a trained model to predict the classifcations of the input data.
    #     """
    #     test_data = nm.NamedMatrix(None, test_examples.rownames, test_examples.colnames + ["class"])
    #     test_data[:,:test_examples.size(1)] = test_examples
    #     test_data[:,-1] = numpy.matrix(test_labels).transpose()
    #     test_arff = WekaML.named_to_arff(test_data)
    #     
    #     temp_arff_data = tempfile.mkstemp(suffix=".arff")[1]
    #     open(temp_arff_data, 'w').write(test_arff)
    #     
    #     weka_output = subprocess.Popen(WEKA_ARGS + \
    #         [self.weka_method, \
    #         "-l", self.model_file, \
    #         "-T", temp_arff_data, \
    #         "-p","first-last" ], \
    #         stdout=subprocess.PIPE).communicate()[0]
    #     
    #     self.weka_output = weka_output
    
    def cross_validate(self, folds=10):
        
        temp_training_arff = tempfile.mkstemp(suffix=".arff")[1]
        tmpfh = open(temp_training_arff, 'w')
        tmpfh.write(self.arff_data)
        tmpfh.close()
        
        temp_threshold_file = tempfile.mkstemp(suffix=".arff")[1]
        self.model_file = tempfile.mkstemp(suffix=".model")[1]
        # We run the weka cross validation and retreive the results
        weka_output = subprocess.Popen(WEKA_ARGS + \
            [self.weka_method, \
            "-t", temp_training_arff, \
            "-x", str(folds), \
            "-d", self.model_file, \
            "-threshold-file", temp_threshold_file, \
            "-threshold-label", "yes"] + self.classifier_params, \
            stdout=subprocess.PIPE).communicate()[0]
        
        train_error = None
        test_error = None
        try:
            train_error = float(weka_output.split('=== Error on training data ===')[1].split('\n')[5].split()[-1])
            test_error  = float(weka_output.split('=== Stratified cross-validation ===')[1].split('\n')[5].split()[-1])
        except IndexError:
            print >> sys.stderr, "Failed to get training and test error out of output"
        
        thresh_results = WekaML.process_threshold_file(temp_threshold_file)
        TPRs = thresh_results['TPR']
        FPRs = thresh_results['FPR']
        PRs = thresh_results['PR']
        REs = thresh_results['RE']
        
        self.plot_data = (TPRs, FPRs, PRs, REs)
        self.weka_output = weka_output
        self.results = {"TrainingError":train_error, "TestError":test_error, \
            "AUROC":thresh_results['AUROC'], "AUPR":thresh_results['AUPR']}
        return self.results
    
    def plot_roc(self, f=None, show_plot=True):
        TPR, FPR, PR, RE = self.plot_data
        figure(1)
        plot(FPR, TPR)
        xlabel('False Positive Rate')
        ylabel('True Positive Rate')
        title('%s ROC Curve' % self.weka_method)
        axis([0,1,0,1])
        if not f is None:
            savefig(f)
        if show_plot:
            show()
        return 1
    
    def plot_pr(self, f=None, show_plot=True):
        TPR, FPR, PR, RE = self.plot_data
        figure(2)
        plot(RE, PR)
        xlabel('Recall')
        ylabel('Precision')
        title('%s PR Curve' % self.weka_method)
        axis([0,1,0,1])
        if not f is None:
            savefig(f)
        if show_plot:
            show()
        return 2

class NaiveBayes(WekaML):
    """
    NaiveBayes WekaML object.
    """
    def __init__(self, examples, labels = None):
        super(NaiveBayes, self).__init__(examples, labels)
        self.weka_method = 'weka.classifiers.bayes.NaiveBayes'
        self.classifier_params = ["-K"]

class Logistic(WekaML):
    """
    Logistic WekaML object.
    """
    def __init__(self, examples, labels = None):
        super(Logistic, self).__init__(examples, labels)
        self.weka_method = 'weka.classifiers.functions.Logistic'
    
    def predict(self, data, labels=None):
        """
        Score the rows of data using the trained coefficients.
        """
        if labels is None:
            scores = nm.NamedMatrix(None, data.rownames, ['Score'])
        else:
            scores = nm.NamedMatrix(None, data.rownames, ['Score', 'Label'])
        
        for i,row in enumerate(data.rownames):
            score = self.coefficients['Intercept']
            for j,col in enumerate(data.colnames):
                score += data[row,col] * self.coefficients[col]
            scores[i,0] = score
            if not labels is None:
                scores[i,1] = labels[i]
        return scores
    
    def process_output(self):
        try:
            coeff_data = self.weka_output.split('Coefficients...')[1].\
                split('Odds Ratios...')[0].split('=\n')[1].split('\n')[:-3]
            self.coefficients = dict()
            for line in coeff_data:
                go_term,coeff = line.split()
                self.coefficients[go_term] = float(coeff)
        except IndexError:
            print >> sys.stderr, "Failed to extract coefficients from weka output."
        
        try:
            odds_data = self.weka_output.split('Odds Ratios...')[1].\
                split('=\n')[1].split('Time taken to build model')[0].split('\n')[1:-3]
        
            self.odds = dict()
            for line in odds_data:
                go_term,odds_ratio = line.split()
                self.odds[go_term] = odds_ratio
        except IndexError:
            print >> sys.stderr, "Failed to extract odds ratios from weka output."
    
    def cross_validate(self, folds=10):
        results = super(Logistic, self).cross_validate(folds)
        self.process_output()
        return results
    
    def test(self, test_examples, test_labels):
        results = super(Logistic, self).test(test_examples, test_labels)
        self.process_output()
        return results

class SVM(WekaML):
    """
    Support Vector Machine WekaML object.
    """
    def __init__(self, examples, labels = None):
        super(SVM, self).__init__(examples, labels)
        self.weka_method = 'weka.classifiers.functions.SMO'
        self.classifier_params.extend(['-K','weka.classifiers.functions.supportVector.RBFKernel'])

def process_learning_point(cls, train_X, train_y, test_X, test_y, index, train_errors, test_errors):
    
    ml = cls(train_X, train_y)
    
    test_result = ml.test(test_X, test_y)
    train_result = ml.test(train_X, train_y)
    
    train_errors[index] = train_result['TestError']
    test_errors[index] = test_result["TestError"]

def partition_matrix(X,y):
    total_pos = int(sum(y))
    group_size = (total_pos - (total_pos % 100))/5
    left_over = set(range(X.size(0)))
    group = list([set() for i in range(5)])
    
    for i in range(5):
        if not i == 0:
            group[i] = copy(group[i-1])
        
        group[i] |= set(random.sample(left_over, group_size))
        left_over -= group[i]
    
    return [X[sorted(g),:] for g in group]

def balance_and_sample_features(features, labels, size):
    positives = random.sample([i for i,x in enumerate(labels) if x == 1.0],size)
    negatives = random.sample([i for i,x in enumerate(labels) if x == 0.0],size)
    indices = positives + negatives
    return features[indices,:]

if __name__ == '__main__':
    pass