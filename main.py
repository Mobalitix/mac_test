import csv
from dataclasses import dataclass
from haversine import haversine, Unit

import folium
from folium.plugins import MarkerCluster, MousePosition

# from numpy import sin, cos, arccos, pi, round
# import math

PATH_TO_DATA = '/Users/en1gm4/Downloads/mactracker_session_2023-07-05-15_52.csv'
# PATH_TO_DATA = '/Users/en1gm4/Downloads/mactracker_session_2023-07-03-18_35.csv'

# PATH_TO_DATA = '/Users/en1gm4/Downloads/mactracker_session_2023-06-16-17_59.csv'
# PATH_TO_DATA = '/Users/en1gm4/Downloads/mactracker_session_2023-06-17-18_15.csv'
# PATH_TO_DATA = '/Users/en1gm4/Downloads/mactracker_session_2023-06-18-13_31.csv'

@dataclass
class Mac_addr:
    mac: str = None
    lat: float = None
    lng: float = None
    t_st: int = None

def to_map(macs: list, datas: list):
    for mm in macs:
        mac_adr = mm[0]
        mac_count = mm[1]
        lat = datas[0].lat
        lng = datas[0].lng
        filename = 'data/' + str(mac_adr) + '-' + str(mac_count) + '.html'
        m = folium.Map(location=[lat, lng], zoom_start=15)
        MousePosition(separator=', ', num_digits=4).add_to(m)
        folium.TileLayer('openstreetmap').add_to(m)
        points = []
        mCluster = MarkerCluster(name=str(mac_adr)).add_to(m)

        for data in datas:
            if data.mac == mac_adr:
                tooltip = str(data.mac) + '<->' + str(data.t_st)
                marker = folium.CircleMarker(
                    location=[data.lat, data.lng],  # coordinates for the marker (Earth Lab at CU Boulder)
                    # popup=pop_up,  # pop-up label for the marker
                    tooltip=tooltip,
                    radius=3,
                    color='red',
                    fill_color='red',
                    fill_opacity=0.8,
                    clustered_marker=True
                ).add_to(mCluster)
                points.append([data.lat, data.lng])

        line = folium.PolyLine(locations=points, color='blue', weight=1,
                               opacity=0.99).add_to(m)

        folium.LayerControl().add_to(m)
        m.save(filename)

def main(path: str):
    start_flag = True
    start_time = 0

    mac_list = []
    you_mac_list = []
    new_mac_list = []
    final_mac_list = []

    data_list = []
    new_data_list = []
    final_data_list = []


    count_unique_mac = 0
    count_all_mac = 0
    with open(path, 'r') as file:
        reader = csv.reader(file)
        for line in reader:
            mac, lat, lon, t_st = line
            count_all_mac += 1
            stamp = t_st[:10]
            new_line = Mac_addr(
                mac=str(mac),
                lat=float(lat),
                lng=float(lon),
                t_st=int(stamp)
            )
            # Если старт сохранить время
            if start_flag:
                start_flag = False
                start_time = int(stamp)
            # Если прошло более 5 минут после старта то в работу
            if (int(stamp) - start_time) > 120:
                # Уникальные мак
                if mac in mac_list:
                    pass
                else:
                    mac_list.append(mac)
                    count_unique_mac += 1

                # Если мак в списке своих устройств то не заносим данные
                if mac in you_mac_list:
                    pass
                else:
                    data_list.append(new_line)
            else:
                # print(mac)
                you_mac_list.append(mac)

        for the_mac in mac_list:
            old_lat = 0
            old_lng = 0
            c_all = 0
            c_raz = 0
            for the_data in data_list:
                if the_data.mac == the_mac:
                    c_all += 1
                    old_coord = (old_lat, old_lng)
                    new_coord = (the_data.lat, the_data.lng)
                    dist = haversine(new_coord, old_coord)
                    # if c_all > 1:
                    #     print(dist)
                    #     print(f'coord1:{the_data.lat}, {the_data.lng}; coord2:{old_lat}, {old_lng}')
                    if dist > 0.066:
                        old_lng = the_data.lng
                        old_lat = the_data.lat
                        new_data_list.append(the_data)
                        c_raz += 1
            if c_raz > 3:
                print(f'mac:{the_mac}, All point:{c_all}, New point:{c_raz}')
                new_mac_list.append(the_mac)

        for the_mac in new_mac_list:
            for the_data in new_data_list:
                if the_data.mac == the_mac:
                    final_data_list.append(the_data)

        mediana = len(final_data_list)/len(new_mac_list)

        for the_mac in new_mac_list:
            count = 0
            # print(the_mac)
            for the_data in final_data_list:
                if the_data.mac == the_mac:
                    count += 1
            if count > mediana*1.5:
                # print(the_mac)
                final_mac_list.append([the_mac, count])

    print('')
    print(f'All mac:{count_all_mac}')
    print(f'Unique mac:{count_unique_mac}')
    print(f'Start data: {start_time}')
    print(f'Количество своих устройств:{len(you_mac_list)}')
    print(f'Кол-во mac где более 2-х точек контакта:{len(new_mac_list)}')
    print(f'Общее количество контактов:{len(final_data_list)}')
    print(f'Среднее кол-во точек на маршруте:{len(final_data_list)/len(new_mac_list)}')
    print('')

    print(f'Количество Мак к проверке:{len(final_mac_list)}')
    for f_mac in final_mac_list:
        print(f'mac:{f_mac[0]}--{f_mac[1]}')

    to_map(final_mac_list, data_list)




if __name__ == '__main__':
    main(PATH_TO_DATA)

