#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple app to feed clock with temperatures
"""

import time
import redis
import appoptics_metrics

appoptics = appoptics_metrics.connect(
        'EcsOPd_2vCayhMCZp9hcNpYyftiH5E9RlZyEyzZ56QpKhTtQ2acWhansMD3u8Pw8Zg_QIgw',
        sanitizer=appoptics_metrics.sanitize_metric_name)

redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

while True:
    try:
        temp_outside_data = appoptics.get_measurements(
                                "temperature",
                                duration=900,
                                resolution=1,
                                tags={
                                    'building': 'terspelt',
                                    'location': 'outside'
                                     })
        temp_float = temp_outside_data.get('series')[0].get('measurements')[0].get('value')
        temp = int(round(temp_float, 0))
        redis_temp = f'{temp:-2}'
        redis.set('temp_outside', redis_temp)
    except Exception as error:
        print(error)
    time.sleep(600)
