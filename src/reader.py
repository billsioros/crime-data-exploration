
import os

import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler

class Reader:

    headers = [
        'INCIDENT_NUMBER',
        'OFFENSE_CODE_GROUP',
        'DISTRICT',
        'SHOOTING',
        'YEAR',
        'MONTH',
        'DAY_OF_WEEK',
        'HOUR',
        'Lat',
        'Long'
    ]

    types = dict(zip(headers, [object, object, object, object, np.int32, np.int32, object, np.int32, np.float64, np.float64]))

    def __init__(self, filename, lat_predicate=lambda entries: entries > 40, lon_predicate=lambda entries: entries < -60):

        if not isinstance(filename, str):
            raise ValueError("'filename' is not an instance of 'str'")

        if not os.path.isdir('out'):
            os.mkdir('out')

        pickled = os.path.splitext(os.path.basename(filename))[0] + '.pkl'

        pickled = os.path.join(os.path.curdir, 'out', pickled)

        if os.path.isfile(pickled):

            print('<LOG>: Loading pickled dataset from', "'" + pickled + "'")

            self.data = pd.read_pickle(pickled)

            print('<LOG>: The dataset consists', len(self.data.index), 'rows and', len(self.data.columns), 'columns')

            return

        print('<LOG>: Processing file', "'" + filename + "'")

        self.data = pd.read_csv(filename, dtype=self.types, skipinitialspace=True, usecols=self.headers)

        print('<LOG>: The dataset consists', len(self.data.index), 'rows and', len(self.data.columns), 'columns')

        self.data['SHOOTING'].fillna('N', inplace=True)

        print('<LOG>: Dropping NaN values')

        self.data.dropna(inplace=True)

        print('<LOG>: Restricting longitude and latitude')

        self.data = self.data[lat_predicate(self.data['Lat']) & (lon_predicate(self.data['Long']))]

        print('<LOG>: Creating column', "'" + 'TIME_PERIOD' + "'")

        self.data['TIME_PERIOD'] = ['Night' if hour <= 6 or hour >= 18 else 'Day' for hour in list(self.data['HOUR'])]

        print('<LOG>: Augmenting the dataset by the factorized equivalent of each column')

        gmin = self.data[['Long', 'Lat']].min().min()
        gmax = self.data[['Long', 'Lat']].max().max()

        for header in self.headers:

            self.data[[header + '_FACTORIZED']] = self.data[[header]].stack().rank(method='dense').unstack()

            self.data[[header + '_FACTORIZED']] = MinMaxScaler((gmin, gmax)).fit_transform(self.data[[header + '_FACTORIZED']])

        print('<LOG>: The dataset consists', len(self.data.index), 'rows and', len(self.data.columns), 'columns')

        print('<LOG>: Saving pickled datafrime to', "'" + pickled + "'")

        self.data.to_pickle(pickled)


    def groupby(self, headers):

        if isinstance(headers, str):
            headers = set([headers])
        elif isinstance(headers, list):
            headers = set(headers)
        else:
            raise ValueError("'headers' must be an instance of 'list'")

        if not headers.issubset(self.headers):
            raise ValueError(headers.difference(self.headers), 'header(s) are not supported')

        return self.data.groupby(list(headers))


if __name__ == '__main__':

    reader = Reader('../data/crime.csv')

    print(reader.groupby(['DAY_OF_WEEK'])['HOUR'].apply(list))

