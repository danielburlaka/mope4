import numpy as np
from itertools import product, combinations
from scipy.stats import t, f

np.set_printoptions(formatter={'float_kind': lambda x: "%.2f"%(x)})



def tableStudent(prob, n, m):
    x_vec = [i*0.0001 for i in range(int(5/0.0001))]
    par = 0.5 + prob/0.1*0.05
    f3 = (m - 1) * n
    for i in x_vec:
        if abs(t.cdf(i, f3) - par) < 0.000005:
            return i


def tableFisher(prob, n, m, d):
    x_vec = [i*0.001 for i in range(int(10/0.001))]
    f3 = (m - 1) * n
    for i in x_vec:
        if abs(f.cdf(i, n-d, f3)-prob) < 0.0001:
            return i

def fisherCriteria(Y_matrix, d):
    if d == N:
        return False
    Sad = m / (N - d) * np.mean(check1 - mean_Y)
    mean_dispersion = np.mean(np.mean((Y_matrix.T - mean_Y) ** 2, axis=0))
    Fp = Sad / mean_dispersion
    if (m-1)*N > 32:
        if N-d > 6:
            return tableFisher(0.95, N, m, d)
        return Fp < tableFisher(0.95, N, m, d)
    if N - d > 6:
        return Fp < tableFisher(0.95, N, m, d)
    return Fp < tableFisher(0.95, N, m, d)

def make_norm_plan_matrix(plan_matrix, matrix_of_min_and_max_x):
    X0 = np.mean(matrix_with_min_max_x, axis=1)
    interval_of_change = np.array([(matrix_of_min_and_max_x[i, 1] - X0[i]) for i in range(len(plan_matrix[0]))])
    X_norm = np.array(
        [[round((plan_matrix[i, j] - X0[j]) / interval_of_change[j], 3) for j in range(len(plan_matrix[i]))]
         for i in range(len(plan_matrix))])
    return X_norm


def cochranCheck(Y_matrix):
    mean_Y = np.mean(Y_matrix, axis=1)
    dispersion_Y = np.mean((Y_matrix.T - mean_Y) ** 2, axis=0)
    Gp = np.max(dispersion_Y) / (np.sum(dispersion_Y))
    fisher = tableFisher(0.95, N, m, 1)
    Gt = fisher / (fisher + (m - 1) - 2)
    return Gp < Gt


def students_t_test(norm_matrix, Y_matrix):
    mean_Y = np.mean(Y_matrix, axis=1)
    dispersion_Y = np.mean((Y_matrix.T - mean_Y) ** 2, axis=0)
    mean_dispersion = np.mean(dispersion_Y)
    sigma = np.sqrt(mean_dispersion / (N * m))
    betta = np.mean(norm_matrix.T * mean_Y, axis=1)
    t = np.abs(betta) / sigma
    if (m - 1) * N > 32:
        return np.where(t > tableStudent(0.95, N, m))
    return np.where(t > tableStudent(0.95, N, m))

flag = False
while not flag:
    try:
        matrix_with_min_max_x = np.array([[15, 45], [30, 80], [15, 45]])
        m = 6
        N = 8
        norm_matrix = np.array(list(product("01", repeat=3)), dtype=np.int)
        norm_matrix[norm_matrix == 0] = -1
        norm_matrix = np.insert(norm_matrix, 0, 1, axis=1)
        plan_matrix = np.empty((8, 3))
        for i in range(len(norm_matrix)):
            for j in range(1, len(norm_matrix[i])):
                if j == 1:
                    if norm_matrix[i, j] == -1:
                        plan_matrix[i, j-1] = 15
                    elif norm_matrix[i, j] == 1:
                        plan_matrix[i, j-1] = 45
                elif j == 2:
                    if norm_matrix[i, j] == -1:
                        plan_matrix[i, j-1] = 30
                    elif norm_matrix[i, j] == 1:
                        plan_matrix[i, j-1] = 80
                elif j == 3:
                    if norm_matrix[i, j] == -1:
                        plan_matrix[i, j-1] = 15
                    elif norm_matrix[i, j] == 1:
                        plan_matrix[i, j-1] = 45
        plan_matr = np.insert(plan_matrix, 0, 1, axis=1)
        Y_matrix = np.random.randint(200 + np.mean(matrix_with_min_max_x, axis=0)[0],
                                     200 + np.mean(matrix_with_min_max_x, axis=0)[1], size=(N, m))
        mean_Y = np.mean(Y_matrix, axis=1)
        combination = list(combinations(range(1, 4), 2))

        for i in combination:
            plan_matr = np.append(plan_matr, np.reshape(plan_matr[:, i[0]]*plan_matr[:, i[1]], (8, 1)), axis=1)
            norm_matrix = np.append(norm_matrix, np.reshape(norm_matrix[:, i[0]]*norm_matrix[:, i[1]], (8, 1)), axis=1)
        plan_matr = np.append(plan_matr, np.reshape(plan_matr[:, 1]*plan_matr[:, 2]*plan_matr[:, 3], (8, 1)), axis=1)
        norm_matrix = np.append(norm_matrix, np.reshape(norm_matrix[:, 1]*norm_matrix[:, 2]*norm_matrix[:, 3], (8, 1)), axis=1)

        if cochranCheck(Y_matrix):
            b_natura = np.linalg.lstsq(plan_matr, mean_Y, rcond=None)[0]
            b_norm = np.linalg.lstsq(norm_matrix, mean_Y, rcond=None)[0]
            check1 = np.sum(b_natura * plan_matr, axis=1)
            check2 = np.sum(b_norm * norm_matrix, axis=1)
            indexes = students_t_test(norm_matrix, Y_matrix)
            print("Matrix Experiment Plan: \n", plan_matr)
            print("Normalized matrix: \n", norm_matrix)
            print("Matrix reviews: \n", Y_matrix)
            print("The average values of Y: ", mean_Y)
            print("Naturalized coefficients: ", b_natura)
            print("Normalized coefficients: ", b_norm)
            print("Check #1: ", check1)
            print("Check #2: ", check2)
            print("Indices of coefficients that satisfy the Student's criterion: ", np.array(indexes)[0])
            print("Student test: ", np.sum(b_natura[indexes] * np.reshape(plan_matr[:, indexes], (N, np.size(indexes))), axis=1))
            if fisherCriteria(Y_matrix, np.size(indexes)):
                flag = True
                print("The regression equation is adequate to the original.")
            else:
                print("The regression equation is inadequate to the original.")
        else:
            print("Dispersion is heterogeneous")
    except ValueError:
        pass
