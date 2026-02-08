# -*- coding: UTF-8 -*-
'''
@Description: Create an application instance.
@LastEditors:
'''
import os
from easyun import create_app


run_env = os.environ.get('FLASK_CONFIG')
app = create_app(run_env)

if __name__ == '__main__':
    app.debug = True
    app.run(host=app.config['HOST'], port=app.config['PORT'])
