import os

class Ecorrection:

    def __init__(self, variable: str, config: dict) -> None:
        
        if variable != '2t':

            raise ValueError(f'{variable} must be \'2t\'')
        
        self.variable = variable

        if not config.keys() <= {'hres_dem_file', 'neighbours_file'}:

            raise KeyError(f'At least \'hres_dem_file\' and \'neighbours_file\' must be in the config dictionary')
        
        self.config = config

        if not os.path.exists(config['hres_dem_file']):

            raise FileNotFoundError(f'{config["hres_dem_file"]} not found')
        
        self.result = None

