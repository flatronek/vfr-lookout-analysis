from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *


def plotZAxis2(dataFrame1, dataFrame2, label1 = "DF1", label2 = "DF2"):
    x1 = dataFrame1[file_header_real_time]
    values1 = dataFrame1[file_header_Z_dps]

    x2 = dataFrame2[file_header_real_time]
    values2 = dataFrame2[file_header_Z_dps]

    title = "Glider Turnings"

    fig, ax = plt.subplots()
    fig.canvas.set_window_title(title)
    # fig.set_size_inches(24.4, 6)
    fig.set_size_inches(21, 9)
    plt.title(title)
    plt.gcf().autofmt_xdate()

    plt.plot(x1, values1, marker='.', linestyle='--')
    plt.plot(x2, values2, marker='.', linestyle='--')

    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend([label1, label2])
    plt.show()


def run():
    cmd_arg_accelerationVector = pd.np.array([-773, 612, 175])

    quat = qt_from_two_vectors(cmd_arg_accelerationVector, z_axis_vector)
    head_gyr_data = load_data_of(dev_head, cat_gyroscope)
    head_gyr_orient_quaternion_data = orientate_data_using_quaternion(head_gyr_data, quat)

    interpolatedData = interpolate_data(head_gyr_orient_quaternion_data, 10)
    plotZAxis2(head_gyr_orient_quaternion_data.df, interpolatedData.df, "Non interpolated", "Interpolated")


if __name__ == "__main__":
    run()