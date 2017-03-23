#!/usr/bin/python
'''
This module does prepare and upload the ALL_WSPR.TXT-format to the influxdb-server

Author : PA7T Clemens Heese clemens at pa7t.nl
         DK5HH Michael Hartje DK5HH at darc.de

Parameters:
 -fi inputfile (ALL_WSPR.TXT-format)
 -fo <optinal> write a file in uploadformat to influxdb (see below)
 -r  Callsign of reporter
 -rl maidenhead locator of reporter
 -u  influxdB user
 -pw influxDB password
 -host influxDB-Server name or IP
 
The upload of the output file (-fo output.daten) could be done with
  curl -X POST 'http://127.0.0.1:8086/write?db=wspr&precision=s' \
  -u user:passwort --data-binary @output.daten

Function:
reading from -fi Infile preparing the ALL_WSPR.TXT-format for upload
uploading with json-client to influxDB-Server -host if not given -fo outfile

Installation:
Prepare the python installation depending on what python version you are
using (2/3)
we need to add the modules in addition to a standeard python installation
influxdb
geohash
You can install these modules with for pythoon 2 with
pip2 install modulename
or for python 3 with
pip3 install modulename

check the installtion in python console
import modulename
(no answer is good news.)

'''

def locator_to_latlong (locator):
    """converts Maidenhead locator in the corresponding WGS84 coordinates
        Args:
            locator (string): Locator, either 4 or 6 characters
        Returns:
            tuple (float, float): Latitude, Longitude
        Raises:
            ValueError: When called with wrong or invalid input arg
            TypeError: When arg is not a string
        Example:
           The following example converts a Maidenhead locator into Latitude and Longitude
           >>> from pyhamtools.locator import locator_to_latlong
           >>> latitude, longitude = locator_to_latlong("JN48QM")
           >>> print latitude, longitude
           48.5208333333 9.375
        Note:
             Latitude (negative = West, positive = East)
             Longitude (negative = South, positive = North)
    """

    locator = locator.upper()

    if len(locator) == 5 or len(locator) < 4:
        raise ValueError

    if ord(locator[0]) > ord('R') or ord(locator[0]) < ord('A'):
        raise ValueError

    if ord(locator[1]) > ord('R') or ord(locator[1]) < ord('A'):
        raise ValueError

    if ord(locator[2]) > ord('9') or ord(locator[2]) < ord('0'):
        raise ValueError

    if ord(locator[3]) > ord('9') or ord(locator[3]) < ord('0'):
        raise ValueError

    if len(locator) == 6:
        if ord(locator[4]) > ord('X') or ord(locator[4]) < ord('A'):
            raise ValueError
        if ord (locator[5]) > ord('X') or ord(locator[5]) < ord('A'):
            raise ValueError

    longitude = (ord(locator[0]) - ord('A')) * 20 - 180
    latitude = (ord(locator[1]) - ord('A')) * 10 - 90
    longitude += (ord(locator[2]) - ord('0')) * 2
    latitude += (ord(locator[3]) - ord('0'))

    if len(locator) == 6:
        longitude += ((ord(locator[4])) - ord('A')) * (2 / 24)
        latitude += ((ord(locator[5])) - ord('A')) * (1 / 24)

        # move to center of subsquare
        longitude += 1 / 24
        latitude += 0.5 / 24

    else:
        # move to center of square
        longitude += 1;
        latitude += 0.5;

    return latitude, longitude

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    Bearing=atan2(sin(dlon)*cos(lat2),
                  cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(dlon))/pi*180
    if Bearing < 0:
        Bearing+=360
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return int(km), int(Bearing)


def wspr_to_upload(in_str,wspr_reporter,wspr_loc_reporter,wspr_comment):

    # in_str = '160310 1942   1 -24 -4.0  7.0395714  PA2W JO22 37            1  6739  -48'

    in_str = in_str.replace('     ', ' ')
    in_str = in_str.replace('    ', ' ')
    in_str = in_str.replace('   ', ' ')
    in_str = in_str.replace('  ', ' ')

    wspr_date, wspr_time, wspr_other, wspr_snr, wspr_dt, wspr_freq, wspr_call, \
         wspr_loc, wspr_pwr, wspr_drift, wspr_rest = in_str.split(' ', 10)

    band_vec = (2200,630,160,80,60,60,40,30,20,17,15,12,10,6)
    freq_vec = (0.1,0.4,1.8,3.5,5.2,5.3,7.0,10.1,14.0,18.1,21.0,24.9,28.1,50.2)
    wspr_band = band_vec[freq_vec.index(round(float(wspr_freq) - 0.05,1))]

#    band_vec = ('LF', 'MW', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m')
#    freq_vec = (0.1, 0.4, 1.8, 3.5, 5.2, 7.0, 10.1, 14.0, 18.1, 21.0, 24.9, 28.1, 50.2)
#    wspr_band = band_vec[freq_vec.index(round(float(wspr_freq) - 0.05, 1))]

    wspr_tuple_time = strptime(wspr_date + wspr_time, "%y%m%d%H%M")
    wspr_time = strftime("%Y-%m-%dT%H:%M:%SZ", wspr_tuple_time)

    loclon_reporter = locator_to_latlong(wspr_loc_reporter)
    wspr_geohash_reporter = Geohash.encode(loclon_reporter[0], loclon_reporter[1], precision=7)

    calckm_az = False
    if wspr_call.find('/') < 0 or wspr_call.find('<') == 0:
        calckm_az = True

    else:
        wspr_dist = -1
        wspr_az = -1
        wspr_drift = wspr_pwr
        wspr_pwr = wspr_loc
        wspr_loc = 'AA00'
        wspr_geohash = '0000'

    if wspr_call.find('<') == 0:
        wspr_call = wspr_call[1:-1]
        if wspr_call.find('..') >= 0:
            wspr_call = "00" + wspr_loc
    # clean up callsign string
    wspr_call = re.sub('[<>]', '', wspr_call)

    if wspr_call.find('..') >= 0:
        wspr_call = "00" + wspr_loc

    if calckm_az:
        loclon = locator_to_latlong(wspr_loc)
        wspr_dist, wspr_az = haversine(loclon_reporter[0], loclon_reporter[1], loclon[0], loclon[1])
        wspr_geohash = Geohash.encode(loclon[0], loclon[1], precision=7)



    json_body = [
        {
            "measurement": "wspr_redpitaya",
            "tags": {
                "reporter": wspr_reporter,
                "call": wspr_call,
                "band": str(wspr_band).rjust(4,'.'),
                "loc": wspr_loc,
                "loc_reporter": wspr_loc_reporter,
                "geohash": wspr_geohash,
                "geohash_reporter": wspr_geohash_reporter,
		"comment": str(wspr_comment)
            },
            "time": wspr_time,
            # fields should be real(integer values -- not strings
            "fields": {
                "snr": int(wspr_snr),
                # limit freq to 6 digits, but keep it a float, not a string!
                "freq": float("%.6f" % float(wspr_freq)),
                "drift": int(wspr_drift),
                "dt": float("%.1f" % float(wspr_dt)),
                "dist": int(wspr_dist),
                "az": int(wspr_az),
                "bandi": int(wspr_band),
                "pwr": int(wspr_pwr) # dBm
            }
        }
    ]
    
    dat_str_local = 'wspr_redpitaya' + \
                    ',reporter=' + str(wspr_reporter) + \
                    ',call=' + wspr_call + \
                    ',band=' + str(wspr_band).rjust(4, '.') + \
                    ',loc=' + wspr_loc + \
                    ',loc_reporter=' + wspr_loc_reporter + \
                    ',geohash=' + str(wspr_geohash) + \
                    ',geohash_reporter=' + str(wspr_geohash_reporter) + \
                    ',comment=\"' + str(wspr_comment)+"\"" + \
                    ' snr=' + str(wspr_snr) + 'i' +\
                    ',freq=' + str("%.6f" % float(wspr_freq)) + \
                    ',drift=' + str(int(wspr_drift)) + 'i' + \
                    ',dt=' + str("%.1f" % float(str(wspr_dt))) + \
                    ',dist=' + str(wspr_dist) + 'i' + \
                    ',az=' + str(wspr_az) + 'i' + \
                    ',bandi=' + str(wspr_band) + 'i' + \
                    ',pwr=' + str(wspr_pwr) + 'i' + \
                    ' ' + str(wspr_time)
                    
    return json_body, dat_str_local

if __name__ == '__main__':  # noqa
    import re
    from time import strftime, strptime
    from math import radians, cos, sin, asin, sqrt, atan2, pi
    from influxdb import InfluxDBClient
    import argparse
    import geohash as Geohash

    parser = argparse.ArgumentParser(
        description='Load ALL_WSPR.TXT like file to Influxdb (or prepare into -fo file)',
        epilog="""... epilog ... with param -fo there is no included upload ...""")

    parser.add_argument(
        '-r', '--reporter',
        type=str,
        help="Reporter call sign",
        default='PA7T',
        required=True)

    parser.add_argument(
        '-rl', '--reporter_locator',
        type=str,
        help="Reporter locator",
        default='JO22FD',
        required=True)
    
    parser.add_argument(
        '-rc', '--reporter_comment',
        type=str,
        help="Reporter comment on configuration i.e. 'ANT=windom, PREAMP=30dB'",
        default='',
        required=False)
    
    parser.add_argument(
        '-u', '--user',
        type = str,
        help = "Username for influxdB-server",
        default='username',
        required=True)

    parser.add_argument(
        '-pw', '--password',
        type = str,
        help = "password for influxDB-Server",
        default='secret_password',
        required=True)

    parser.add_argument(
        '-H', '--host',
        type = str,
        help = "influxdB-Server-name or IP",
        default='thehost.home.net',
        required=True)

    parser.add_argument(
        '-p', '--port',
        type = int,
        help = "influxdB-Server port",
        default= 8086,
        required=True)

    group = parser.add_argument_group('files')

    parser.add_argument(
        '-fi',
        type=str,
        help="filename of ALL_WSPR.TXT-file",
        default='ALL_WSPR.TXT')

    parser.add_argument('-fo',
        type=str,
        help="filename to output",
        default=False)

    args = parser.parse_args()
    # try to open input file
    try:
        f = open(args.fi, "r")
    except (IOError, OSError):
        print("Error: Cannot open file {} for reading!\n".format(args.fi))
        exit(1)
    else:
        print("Processing file {} ...".format(args.fi))
        try:
            if args.fo:
                fout = open(args.fo,'a')
                print("output to {} ...".format(args.fo))
            # open connection to Influxdb, fixed DB "wspr"
            else:
                client = InfluxDBClient(args.host, args.port, args.user, 
                                    args.password, 'wspr')
            # iterate over lines
            wspr_no = sum(1 for line in f)
            f.seek(0)
            i = 1
            for in_str in f:
#                print "{}/{}".format(i,wspr_no)
                #print(in_str)
                json_body,dat_str = wspr_to_upload(in_str,args.reporter,args.reporter_locator,args.reporter_comment)
                #print(json_body)

                if args.fo:
                    fout.write(dat_str + '\n')
                else:
                    # submit spot to Influxdb
                    ret = client.write_points(json_body)
                i=i+1
            if args.fo:
                print( str(wspr_no) + " spot for influxdB to file.")
            else:    
                print( str(wspr_no) + " spot Uploads to influxdB done.")
        finally:
            f.close()
            if args.fo:
                fout.close()
