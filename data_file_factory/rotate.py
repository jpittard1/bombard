
import numpy as np

class Rotate:

    def about_x(array, theta_deg, round_dp = False):

        theta = theta_deg*np.pi/180
        rotation = np.array([[1,0,0],
                    [0,np.cos(theta),-np.sin(theta)],
                    [0, np.sin(theta), np.cos(theta)]])
        if round_dp == False:
            return np.dot(rotation, array)
        else:
            data = [round(i,round_dp) for i in np.dot(rotation,array)]
            return np.array(data)


    def about_y(array, theta_deg, round_dp = False):

        theta = theta_deg*np.pi/180
        rotation = np.array([[np.cos(theta),0,np.sin(theta)],
                    [0,1,0],
                    [-np.sin(theta),0, np.cos(theta)]])

        if round_dp == False:
            return np.dot(rotation, array)
        else:
            data = [round(i,round_dp) for i in np.dot(rotation,array)]
            return np.array(data)


    def about_z(array, theta_deg, round_dp = False):

        theta = theta_deg*np.pi/180
        rotation = np.array([[np.cos(theta),-np.sin(theta),0],
                    [np.sin(theta),np.cos(theta),0],
                    [0,0,1]])

        if round_dp == False:
            return np.dot(rotation, array)
        else:
            data = [round(i,round_dp) for i in np.dot(rotation,array)]
            return np.array(data)

    def general(theta_deg_list, round_dp = False):

        thetas = [theta_deg*np.pi/180 for theta_deg in theta_deg_list]
        print(thetas)
        rotation_x = np.array([[1,0,0],
                    [0,np.cos(thetas[0]),-np.sin(thetas[0])],
                    [0, np.sin(thetas[0]), np.cos(thetas[0])]])
        rotation_y = np.array([[np.cos(thetas[1]),0,np.sin(thetas[1])],
                    [0,1,0],
                    [-np.sin(thetas[1]),0, np.cos(thetas[1])]])

        rotation_z = np.array([[np.cos(thetas[2]),-np.sin(thetas[2]),0],
                    [np.sin(thetas[2]),np.cos(thetas[2]),0],
                    [0,0,1]])

        rotation = np.dot(rotation_z, np.dot(rotation_y, rotation_x))

        return rotation

class Shift:

    def centre(full_arr, round_dp = 4):

        x_centre = round(((max(full_arr[:,-3]) + min(full_arr[:,-3]))/2),round_dp) 
        y_centre = round(((max(full_arr[:,-2]) + min(full_arr[:,-2]))/2),round_dp)
        z_centre = round(((max(full_arr[:,-1]) + min(full_arr[:,-1]))/2),round_dp)
        z_min = round(min(full_arr[:,-1]),round_dp)

        shift_arr = np.ones([full_arr.shape[0],4])
      
        shift_arr[:,0] = shift_arr[:,0]*0
        shift_arr[:,1] = shift_arr[:,1]*x_centre
        shift_arr[:,2] = shift_arr[:,2]*y_centre
        shift_arr[:,3] =shift_arr[:,3]*(z_centre)

        return full_arr - shift_arr

    def translate(full_arr, translation, round_dp = 4):

        shift_arr = np.ones([full_arr.shape[0],4])

        shift_arr[:,0] = shift_arr[:,0]*0
        shift_arr[:,1] = shift_arr[:,1]*translation[0]
        shift_arr[:,2] = shift_arr[:,2]*translation[1]
        shift_arr[:,3] = shift_arr[:,3]*translation[2]

        return full_arr + shift_arr

    def origin(full_arr, round_dp = 4):

        x_min = min(full_arr[:,1])
        y_min = min(full_arr[:,2])
        z_min = min(full_arr[:,3])

        shift_arr = np.ones([full_arr.shape[0],4])

        shift_arr[:,0] = shift_arr[:,0]*0
        shift_arr[:,1] = shift_arr[:,1]*x_min
        shift_arr[:,2] = shift_arr[:,2]*y_min
        shift_arr[:,3] = shift_arr[:,3]*z_min

        return full_arr - shift_arr





