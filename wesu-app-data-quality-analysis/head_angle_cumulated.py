from head_angle_peaks_detection import prepareGliderGyroData, filterAndCumulateData
from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *

# 2017-05-17
head_neutral_acc_vector = pd.np.array([-1000, -125, 170])
glider_neutral_acc_vector = pd.np.array([-200, -54, 970])

head_gyro_calibration_vector = pd.np.array([0.4, -0.9, -1.6])
glider_gyro_calibration_vector = pd.np.array([1.6, -3.6, -3.3])

def plot(originalHeadData):
    fig, ax = plt.subplots()
    fig.set_size_inches(24.4, 6)

    # cumulatedData
    plt.plot(originalHeadData.df[file_header_real_time], originalHeadData.df[file_header_Z_dps], marker='.', linestyle='--')

    plt.title("Cumulative trapeze integration")
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend(["Head data"])
    plt.show()


def run():
    startTime = 550000
    endTime = 1700000

    headTimeCutData = prepareGliderGyroData(dev_head, head_neutral_acc_vector, head_gyro_calibration_vector,
                                            startTime, endTime)

    cumulatedData = filterAndCumulateData(headTimeCutData)

    plot(cumulatedData)


if __name__ == "__main__":
    run()
