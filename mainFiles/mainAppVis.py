from core.MultiApp import App

smalls={'built on': 'built on: BUILDDATE',
        'git repo.':"https://gitlab.cern.ch/wraight/itk-web-apps",
        'docker repo.':"https://hub.docker.com/repository/docker/kwraight/general-multi-app",
        'API info.': "https://uuos9.plus4u.net/uu-dockitg01-main/78462435-41f76117152c4c6e947f498339998055/book/page?code=uuSubAppMainUuCmdList"}

myapp = App("DataVis App", "Multi-theme DataVis App", smalls)

myapp.main()
