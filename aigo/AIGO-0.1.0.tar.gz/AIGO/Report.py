from pylab import *

from time import strftime

from AIGO import allAspect

class ReportFA():

    def __init__(self, **args):

        # set any keyword valued parameters
        for k,v in args.items():
            self.__dict__[k] = v

    def printStatistics(self, allFA, exportList):
        for aspect in allAspect:
            
            #Write Headers
            print "\n=========================================================================="
            print "Properties of %s Functional Annotations for %s" % (self.organism, aspect)
            print "\tMeasure",
            for name in [FA.name for FA in allFA]:
                print"\t%s" % name,

            #Write Measures
            for meas in exportList:
                print "\n\t%s" % meas,

                for FA in allFA:
                    if FA.has_key(meas):
                        d=FA[meas][aspect]
                        if type(d)==list:
                            d=mean(d)

                        print "\t%.2f" % d,
                    else:
                        print "\t-",
            print "\n=========================================================================="
    

    def saveStatistics(self, allFA, exportList):
        import xlwt

        title_f = xlwt.Font()
        title_f.height = 200
        title_f.name = 'Verdana'
        title_f.bold= True
        title_xf = xlwt.easyxf('align: vert centre, horiz center')
        title_xf.font = title_f

        bold_f = xlwt.Font()
        bold_f.height = 180
        bold_f.name = 'Times New Roman'
        bold_f.bold= True
        bold_xf = xlwt.easyxf('align: vert centre, horiz center')
        bold_xf.font = bold_f


        number_xf=xlwt.easyxf('align: vert centre, horiz center')
        number_xf.num_format_str="0.00"
        
        norm_xf=xlwt.easyxf('align: vert centre, horiz center')

        
        wb = xlwt.Workbook()

        for aspect in allAspect:
            
            ws=wb.add_sheet(aspect)

            #Write Headers        
            tit="Properties of %s Functional Annotations for %s" % (self.organism, aspect)
            ws.col(0).width = len(tit) * 256            
            ws.write(0,0, tit , title_xf)
            ws.write(1,0, "Measure", bold_xf)
            for i,name in enumerate([FA.name for FA in allFA]):
                ws.write(1,1+i, name, bold_xf)
                ws.col(1+i).width = 0x0d00 + 210

            offset=2
            #Write Measures
            for meas in exportList:
                ws.write(offset,0, meas, norm_xf)

                for i,FA in enumerate(allFA):
                    d=FA[meas][aspect]
                    if type(d)==list:
                        d=mean(d)
                        
                    ws.write(offset,1+i, d, number_xf)

                offset=offset+1

                
        fileName="%s/export_%s_%s.xls" % (self.outDir, self.name, self.organism)
        wb.save(fileName)

        



