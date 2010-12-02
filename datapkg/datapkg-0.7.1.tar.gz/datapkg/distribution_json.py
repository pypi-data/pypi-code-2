

class JsonDistribution(DistributionBase):
    @classmethod
    def load(self, path):
        pkg = Package()
        pkg.installed_path = path 
        fp = os.path.join(path, 'metadata.json')

