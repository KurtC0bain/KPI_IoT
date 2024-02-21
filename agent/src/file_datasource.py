import csv
from csv import reader 
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
import config


class FileDatasource:
    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
    ) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename

    def read(self) -> list[AggregatedData]:
        #The method returns data received from the sensors
        accelerometer_data = self._read_accelerometer_data()
        gps_data = self._read_gps_data()

        # Determine the minimum length of data to avoid IndexError
        min_length = min(len(accelerometer_data), len(gps_data))
        
        aggregated_data_list = []
        for i in range(min_length):
            aggregated_data_list.append(
                AggregatedData(
                    accelerometer_data[i],
                    gps_data[i],
                    datetime.now(),
                    config.USER_ID,
                )
            )
            
        return aggregated_data_list

    def _read_accelerometer_data(self) -> list[Accelerometer]:
        accelerometer_data = []
        with open(self.accelerometer_filename, 'r') as file:
            csv_reader = reader(file)
            next(csv_reader)  # Skip header if present
            for row in csv_reader:
                x, y, z = map(int, row)
                accelerometer_data.append(Accelerometer(x, y, z))
        return accelerometer_data

    def _read_gps_data(self) -> list[Gps]:
        gps_data = []
        with open(self.gps_filename, 'r') as file:
            csv_reader = reader(file)
            next(csv_reader)  # Skip header if present
            for row in csv_reader:
                longitude, latitude = map(float, row)
                gps_data.append(Gps(longitude, latitude))
        return gps_data

    # def read(self) -> AggregatedData:
    #     #The method returns data received from the sensors
    #     accelerometer_data = self._read_accelerometer_data()
    #     gps_data = self._read_gps_data()
    #     return AggregatedData(
    #         accelerometer_data,
    #         gps_data,
    #         datetime.now(),
    #         config.USER_ID,
    #     )

    # def _read_accelerometer_data(self) -> Accelerometer:
    #     data_list = []
    #     with open(self.accelerometer_filename, 'r') as csv_file:
    #         csv_reader = csv.DictReader(csv_file)
    #         for row in csv_reader:
    #             data_list.append(row)
    #     return data_list

    # def _read_gps_data(self) -> Gps:
    #     data_list = []
    #     with open(self.gps_filename, 'r') as csv_file:
    #         csv_reader = csv.DictReader(csv_file)
    #         for row in csv_reader:
    #             data_list.append(row)
    #     return data_list

    def startReading(self, *args, **kwargs):
        """The method must be called before reading data"""
        pass

    def stopReading(self, *args, **kwargs):
        """The method should be called to stop reading data"""
        pass