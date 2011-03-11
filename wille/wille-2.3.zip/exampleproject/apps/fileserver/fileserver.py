"""fileserver.py - Simple fileserver"""

import wille
from wille.views import ServeFiles

urls = (
	("/(.*)", ServeFiles, 'shared'),
)

# Standalone launch
if __name__ == "__main__": wille.run_app(urls)
