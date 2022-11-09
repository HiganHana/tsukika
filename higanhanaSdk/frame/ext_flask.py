import flask
from higanhanaSdk.frame.config import DcMfConfig
from higanhanaSdk.frame.i import mfi
from higanhanaSdk.frame.keys import DcMainframeKeys, DcMainframeCore
from threading import Thread
import os
from higanhanaSdk.utils.iport import import_objs

class flaskExtension(mfi):
    @mfi._parse_params
    @mfi._save_flag
    def setup_flask(self,
        flask_host : str,
        flask_port : int,
        flask_debug : bool,
        default_flask_cogs : str,
        flask_blueprint_register_prefix : bool
    ):   
        from flask import Flask
        
        self._flask_app = Flask(__name__)
        
        # load flask cogs
        for blueprint in import_objs(os.path.join(self.project_name, default_flask_cogs), flask.Blueprint):
            if flask_blueprint_register_prefix:
                self._flask_app.register_blueprint(blueprint, url_prefix=f"/{blueprint.name}")
            else:
                self._flask_app.register_blueprint(blueprint)
        
        
        def flask_run():
            self._flask_app.run(
                host=flask_host,
                port=flask_port,
                debug=flask_debug
            )
        self.flask_thread = Thread(target=flask_run)

        return lambda : self.flask_thread.start()
    
    @mfi._parse_params
    def init_flask(self,
        default_flask_cogs : bool,
    ):
        os.makedirs(os.path.join(self.project_name, default_flask_cogs), exist_ok=True)
    
    @mfi._parse_params
    @mfi._save_flag
    def setup_flask_cold_trigger(self,
        cold_trigger_token : str
                                 
    ):
        self.setup_flask()

        from flask import request
        
        def cold_trigger():
            if request.headers.get("token") != cold_trigger_token:
                return
            
            import os
            self.logger.info("Cold trigger activated")
            os.system("kill 1")    
            
        
        self._flask_app.add_url_rule(
            "/COLD_TRIGGER/", methods=["POST"],
            view_func=cold_trigger
        )
        
        