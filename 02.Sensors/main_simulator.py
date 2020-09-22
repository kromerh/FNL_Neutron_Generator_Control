import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/pi/FNL_Neutron_Generator_Control/02.Sensors/01.HV_Dose_twofast-rpi3-0/Python/')
sys.path.insert(1, '/home/pi/FNL_Neutron_Generator_Control/02.Sensors/02.Pressure_twofast-rpi3-3/Python/')

from HV_Dose_Simulator import HV_Dose_Simulator
from Pressure_Simulator import Pressure_Simulator


hv_dose =  HV_Dose_Simulator()
hv_dose.main()

pressure = Pressure_Simulator()
pressure.simulate()