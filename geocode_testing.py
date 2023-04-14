

'''Geocoding Test Script V1
R. Ballard 4/13/23'''

'''Uses method described here: https://towardsdatascience.com/transform-messy-address-into-clean-data-effortlessly-using-geopy-and-python-d3f726461225
   Uses Virginia SCC Business Entity Corps.csv dataset available here: https://cis.scc.virginia.gov/DataSales/DownloadBEDataSalesFile  '''





import configparser
import pandas
import numpy
from geopy.geocoders import Nominatim


config = configparser.ConfigParser()

config_items = config.read('secret/config.ini')


#Read corps dataset
messy_address = pandas.read_csv(config['FILE_PATHS']['infile'],index_col=False)

#Subset data with fixed seed
messy_address = messy_address.sample(n=500,random_state=48377)

#Declare API endpoint handler
geolocator = Nominatim(user_agent=config['API_STRINGS']['email'])

#Try-Except wrapper for geocoding call
def extract_clean_address(address):
    try:
        location = geolocator.geocode(address)
        return location.address
    except:
        return ''

#Concatenate address fields, empty fields look like "xxxx,    ,xxxx,xxx" etc, strip below gives better performance
messy_address['Raw Address'] = messy_address[['Street1', 'Street2', 'City', 'State', 'Zip']].apply(lambda x: ','.join(x), axis=1)

#Concatenate address fields, empty fields dropped like "xxxx,xxxx,xxx" etc, addresses wholly left blank will be '' (empty string)
messy_address['Raw Address'] = messy_address[['Street1', 'Street2', 'City', 'State', 'Zip']].agg(lambda x: ', '.join(word for word in x if word.strip()).strip() , axis=1)

#Geocode with apply custom function
messy_address['clean address'] = messy_address.apply(lambda x: extract_clean_address(x['Raw Address']) , axis=1  )

#Geocode with vectorized function, doesn't appear to give gains
vectorclean = numpy.vectorize(extract_clean_address)
messy_address['clean address'] = vectorclean(messy_address['Raw Address'])

messy_address.to_csv(config['FILE_PATHS']['outfile'])
