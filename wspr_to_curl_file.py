
# coding: utf-8

# In[140]:




# In[141]:


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


# In[142]:


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


# In[143]:


def wspr_to_json(in_str,wspr_reporter,wspr_loc_reporter,wspr_comment):

    # in_str = '160310 1942   1 -24 -4.0  7.0395714  PA2W JO22 37            1  6739  -48'
    wspr_date, wspr_time, wspr_other, wspr_snr, wspr_dt, wspr_freq, wspr_call, wspr_loc,         wspr_pwr, wspr_drift, wspr_rest = re.split(r'[;,\s]\s*', in_str,10)

    band_vec = (2200,630,160,80,60,60,40,30,20,17,15,12,10,6)
    freq_vec = (0.1,0.4,1.8,3.5,5.2,5.3,7.0,10.1,14.0,18.1,21.0,24.9,28.1,50.2)
    wspr_band = band_vec[freq_vec.index(round(float(wspr_freq) - 0.05,1))]

#    band_vec = ('LF', 'MW', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m')
#    freq_vec = (0.1, 0.4, 1.8, 3.5, 5.2, 7.0, 10.1, 14.0, 18.1, 21.0, 24.9, 28.1, 50.2)
#    wspr_band = band_vec[freq_vec.index(round(float(wspr_freq) - 0.05, 1))]

    wspr_tuple_time = strptime(wspr_date + wspr_time, "%y%m%d%H%M")
    wspr_time = strftime("%Y-%m-%dT%H:%M:%SZ", wspr_tuple_time)
    wspr_epoch = "%.0f" % (calendar.timegm(wspr_tuple_time))

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
            "measurement": "wspr_main",
            "tags": {
                "reporter": wspr_reporter,
                "band": str(wspr_band).rjust(4,'.'),
                "loc_reporter": wspr_loc_reporter,
                "geohash_reporter": wspr_geohash_reporter,
                "comment": str(wspr_comment)
            },
            "time": wspr_time,
            # fields should be real(integer values -- not strings
            "fields": {
                "call": wspr_call,
                "loc": wspr_loc,
                "geohash": wspr_geohash,
                "snr": int(wspr_snr),
                "freq": float("%.6f" % float(wspr_freq)), # limit freq to 6 digits, but keep it a float, not a string!
                "drift": int(wspr_drift),
                "dt": float("%.1f" % float(wspr_dt)),
                "dist": int(wspr_dist),
                "az": int(wspr_az),
                "pwr": int(wspr_pwr) # dBm
            }
        }
    ]

    return json_body


# In[144]:


def json_curl_str(json_body):
#json_body = [
#{
#        "fields": {
#            "az": 217,
#            "call": "EA4URA",
#            "dist": 1497,
#            "drift": 0,
#            "dt": -0.6,
#            "freq": 7.040134,
#            "geohash": "ezjm9dq",
#            "loc": "IN80CI",
#            "pwr": 20,
#            "snr": -22
#        },
#        "measurement": "wspr_main",
#        "tags": {
#            "band": "..40",
#            "comment": "Wdm",
#            "geohash_reporter": "u1hvw66",
#            "loc_reporter": "JO31LO",
#            "reporter": "DL2ZZ"
#        },
#        "time": "2018-01-26T17:58:00Z"
#    }
#]

    curl_str = json_body[0]['measurement']

    for tag in json_body[0]['tags']:
        curl_str = curl_str + "," + tag + "=" + str(json_body[0]['tags'][tag])

    i=0
    for field in json_body[0]['fields']:
        if(i==0):
            curl_str = curl_str + " " + field + "=" + str(json_body[0]['fields'][field])
        else:
            curl_str = curl_str + "," + field + "=" + str(json_body[0]['fields'][field])
        i = i + 1

    curl_str = curl_str + ' ' + json_body[0]['time']

    return curl_str


# In[150]:


if __name__ == '__main__': # noqa

    import re
    import json
    import calendar
    from time import strftime, strptime, mktime
    from math import radians, cos, sin, asin, sqrt, atan2, pi
    import geohash as Geohash
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert ALL_WSPR.TXT like file to prepare for curl uploading to wsprlive.net Influxdb',
        epilog="""... epilog ...""")

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

    group = parser.add_argument_group('files')

    parser.add_argument(
        '-fi',
        type=str,
        help="filename of ALL_WSPR.TXT-file",
        default='ALL_WSPR.TXT')

    args = parser.parse_args()

    try:
        f = open(args.fi, "r")
        #print(args)
    except (IOError, OSError):
        print("Error: Cannot open file {} for reading!\n".format(args.fi))
        exit(1)
    else:
        #print("Processing file {} ...\n".format(args.fi))
        try:
            # iterate over lines
            wspr_no = sum(1 for line in f)
            f.seek(0)
            i = 1
            for in_str in f:
                if args.reporter_comment:
                    comment = args.reporter_comment
                else:
                    comment = ''
            #print(in_str)
                json_body = wspr_to_json(in_str,args.reporter,args.reporter_locator,comment)
                #print(json.dumps(json_body, indent=2, sort_keys=True))
                curl_str = json_curl_str(json_body)
                print(curl_str)
                i=i+1
        finally:
            f.close()
