import os
import inspect
import redis
from pathlib import Path
from datetime import datetime


class ConfigurationClient:
    """
    Provides synchronization between PCs and persistent storage of values
    Currently based on Redis but could be extended to other backends
    """
    _experiment_classes = ['UniVie', 'External', 'IP']
    def __init__(self, host, port=6379, token=None):
        self.client = redis.Redis(host=host, port=port, password=token)
        try:
            self.client.ping()
        except redis.exceptions.ConnectionError:
            raise ValueError(f'Could not connect to server: {host}:{port}')

    @property
    def PI_name(self):
        res = self.client.get('PI_name')
        if res is None:
            raise ValueError('PI_name not set')
        return res.decode('utf-8')
    
    @PI_name.setter
    def PI_name(self, value):
        self.client.set('PI_name', value)

    @property
    def project_id(self):
        res = self.client.get('project_id')
        if res is None:
            raise ValueError('project_id not set')
        return res.decode('utf-8')

    @project_id.setter
    def project_id(self, value):
        self.client.set('project_id', value)

    @property
    def last_dataset(self) -> Path | None:
        """
        Path to the last dataset that was recorded
        """
        res = self.client.get('last_dataset')
        if res is None:
            return None
        return Path(res.decode('utf-8'))
    
    @last_dataset.setter
    def last_dataset(self, value):
        self.client.set('last_dataset', value)

    
    @property
    def file_id(self):
        """
        Unique identifier for the current dataset
        """
        res = self.client.get('file_id')

        #if not set we set it to 0
        if res is None:
            self.client.set('file_id', 0)
            return 0
        return int(res)
    
    @file_id.setter
    def file_id(self, value):
        self.client.set('file_id', value)

    def incr_file_id(self):
        self.client.incr('file_id')

    @property
    def base_data_dir(self):
        res = self.client.get('base_data_dir')
        if res is None:
            raise ValueError('base_data_dir not set')
        return Path(res.decode('utf-8'))
    
    @base_data_dir.setter
    def base_data_dir(self, value: Path|str):
        value = Path(value)
        self.client.set('base_data_dir', value.as_posix())
    
    @property
    def data_dir(self):
        """
        Directory where the current experiment will be stored.
        Computed from the configured experiment
        TODO! Do we need the support for a custom directory
        """
        path = Path(self.base_data_dir) / self.experiment_class / self.PI_name / self.project_id / self.today
        return path
    

    @property
    def working_dir(self):
        """
        Directory where output of data analysis will be stored
        """
        path = Path(self.base_data_dir) / self.experiment_class / self.PI_name / self.project_id
        return path

    @property
    def fname(self):
        """
        Filename for the current dataset
        generated from the configured experiment and the current date
        """
        res = self.client.get('measurement_tag')
        if res is None:
            raise ValueError('fname not set')
        s = f'{self.file_id:03d}_{self.project_id}_{res.decode("utf-8")}_{self.today}.h5'
        return s
    
    @property
    def measurement_tag(self):
        """
        Tag for the current measurement
        """
        res = self.client.get('measurement_tag')
        if res is None:
            raise ValueError('measurement_tag not set')
        return res.decode('utf-8')
    
    @measurement_tag.setter
    def measurement_tag(self, value):
        self.client.set('measurement_tag', value)


    @property
    def experiment_class(self):
        res = self.client.get('experiment_class')
        if res is None:
            raise ValueError('experiment_class not set')
        return res.decode('utf-8')
    
    @experiment_class.setter
    def experiment_class(self, value):
        if value not in ConfigurationClient._experiment_classes:
            raise ValueError(f'Invalid experiment class. Possible values are: {ConfigurationClient._experiment_classes}. Got: {value}')
        self.client.set('experiment_class', value)

    @property
    def today(self):
        """
        Returns the current date in the format YYYY-MM-DD
        #TODO! should we set this manually instead for experiments crossing over midnight?
        """
        return datetime.now().strftime('%Y-%m-%d')

    def __repr__(self) -> str:
        s = f"""
        Configuration:
        \tPI_name: {self.PI_name}
        \tproject_id: {self.project_id}
        \texperiment_class: {self.experiment_class}
        \tdata_dir: {self.data_dir}
        \tfname: {self.fname}

        \tlast_dataset: {self.last_dataset}
        """
        return inspect.cleandoc(s)


if __name__ == '__main__':
    #Server to connect to and authentication token
    try:
        token = os.environ['REDIS_TOKEN']
    except KeyError:
        raise ValueError('Please set the REDIS_TOKEN environment variable')    
        exit(1)
        
    host = 'detpi02'

    cfg = ConfigurationClient(host, token=token)

    #Reset all values
    cfg.client.flushall()

    cfg.PI_name = 'Erik'
    cfg.project_id = 'epoc'
    cfg.experiment_class = 'UniVie'
    cfg.base_data_dir = '/data/jungfrau/instruments/jem2100plus'
    cfg.measurement_tag = 'Lysozyme'

    print(cfg)
