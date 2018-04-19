from vfr_data_analysis.quaterion_utils import *
from vfr_data_analysis.constants_and_utils import *
from vfr_data_analysis.transition_matrix_utils import *
from vfr_data_analysis.ploting import *
from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *

if __name__ == "__main__":
    glider_mag_data = load_data_of(dev_glider, cat_magnetometer)
    glider_mag_no_spikes_data = filter_out_spikes(glider_mag_data)
    glider_turnings = detect_glider_turnings(glider_mag_no_spikes_data)

    print(glider_mag_data.df.columns)
    print(glider_mag_data.df.index)

    print(glider_turnings.df.columns)
    print(glider_turnings.df.index)

    pd.set_option('display.max_rows', 5)
    print(glider_turnings.df)
    pd.reset_option('display.max_rows')

    plotData(glider_mag_data, "Wskazania magnetometru z czujnika umieszczonego na szybowcu")
    plotData(glider_mag_no_spikes_data, "Wskazania magnetometru z czujnika umieszczonego na szybowcu, po usunięciu szumu")
    plotData(glider_turnings, "Wykryte skręty szybowca")
    export_glider_turnings_to_csv(glider_turnings)
