import xmltodict
import numpy as np


# x_zoom, y_zoom = 0.7, 0.7
# x_offset, y_offset = 50, 50
# z_mat, z_lift = 0.3, 1
# cut_speed, move_speed = 36000, 36000


# print('1.0 zoom = 10mm lines (CHECK!!!!)')
# print('x_zoom: ', x_zoom, ' y_zoom: ', y_zoom)
# print('x_offset: ', x_offset, ' y_offset: ', y_offset)
# print('z_mat: ', z_mat, ' z_lift: ', z_lift)
# print('cut_speed: ', cut_speed, ' move_speed: ', move_speed)



def gen_gcode(filename, x_zoom=0.7, y_zoom = 0.7, x_offset=50, y_offset=50,\
              z_mat=0.3, z_lift=1, cut_speed=36000, move_speed=36000):
    

    with open(filename) as f:
        xml = f.read().replace('\n', '')

    d = xmltodict.parse(xml)
    d = dict(d)


    gcode = """
    ;START
    G21;
    G90;
    G0 Z1 F6000;


    """

    gsub = []
    glist = []
    GX_i, GX_l, GY_i, GY_l = 0, 0, 0, 0
    first = True

    for p in d['svg']['path']:
        for m in p['@d'].split('M'):
            try:
                for i, l in enumerate(m.split('L')):
                    GX_o, GY_o = l.split(',')
                    GX_o, GY_o = float(GX_o), float(GY_o)
                    
                    if GX_o or GY_o:
                        #print(type(GY_o))
                        #print(GX_o, GY_o)
                        GX_o, GY_o = (float(GX_o)/2.857142857143)*x_zoom, (float(GY_o)/2.857142857143)*y_zoom
                        # if first or ((GX_l-20)>GX_o):
                        #     #print(GX_o, GY_o)
                        #     GX_i, GY_i = GX_o-x_offset-5, 5-y_offset
                        GX, GY = GX_o+x_offset-5, abs(GY_o-350)+(5-y_offset)
                        #print(GX,GY)
                        GX_l, GY_l = GX_o, GY_o
                        if first:
                            #gcode += f'G1 X{GX} Y{GY} F{move_speed};\n'
                            #gcode += f'pause\n'
                            first = False
                        if i:
                            gcode += f'G1 X{GX} Y{GY} F{cut_speed};\n'
                            gsub.append([GX, GY])
                        else: # Initial Response
                            gcode += f'G0 Z{z_lift} F{move_speed};\n'
                            gcode += f'G0 X{GX} Y{GY} F{move_speed};\n'
                            gcode += f'G0 Z{z_mat} F{cut_speed};\n'
                            if len(gsub):
                                glist.append(gsub)

                            gsub = [[GX, GY]]
            except:
                pass
            gcode += f'G0 Z1 F{cut_speed};\n'

    if len(gsub):
        glist.append(gsub)
    # gcode += 'G0 Z100 F6000;\n'
    gcode += 'G28 X Y Z;\n'

    gcode_filename = filename[:-3]+'gcode'

    with open(gcode_filename, 'w') as text_file:
        text_file.write(gcode)

    return gcode_filename, gcode, glist

# print(gcode)

# print('0:::::::', d['svg']['path'][0]['@d'])
# print('1:::::::', d['svg']['path'][1]['@d'])
# print('2:::::::', d['svg']['path'][2]['@d'])
# print('3:::::::', d['svg']['path'][3]['@d'])

# G1 X61.13513513513513 Y249.83783783783784 F6000
# G0 Z1 F6000
# G0 X64.05405405405406 Y249.83783783783784 F6000
# G0 Z0.3 F6000
