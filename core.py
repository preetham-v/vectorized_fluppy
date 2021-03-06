import numpy as np
import time
import os
import sys
import matplotlib.pyplot as plt
from scipy.signal import convolve


def init_Pop(conf):
    n = conf[0]
    choice_of_u = conf[1]
    nTasks = conf[2]
    compCap = conf[3]
    insight = conf[4]
    exp_eff = conf[5]
    pop_size = conf[6]
    mutation_prob = conf[7]
    crossover_prob = conf[8]
    number_of_gen = conf[9]
    alpha = conf[10]
    beta = conf[11]
    population = np.random.randint(nTasks, size=(pop_size,n,n,compCap))
    return population

def uf(res):
    return np.sum(res)

def grid_uf(res_grid,conf):
    n = conf[0]
    choice_of_u = conf[1]
    nTasks = conf[2]
    compCap = conf[3]
    insight = conf[4]
    exp_eff = conf[5]
    pop_size = conf[6]
    mutation_prob = conf[7]
    crossover_prob = conf[8]
    number_of_gen = conf[9]
    alpha = conf[10]
    beta = conf[11]
    ufs = np.zeros((n,n))
    for i in range(res_grid.shape[0]):
        for j in range(res_grid.shape[1]):
            ufs[i,j] = uf(res_grid[i,j])
    return ufs

# This function returns the resource and donation vectors after processing the genome (NOTE: Zero task has no resource acquisition)
def genome_to_res_and_donate(genome,conf):
    n = conf[0]
    choice_of_u = conf[1]
    nTasks = conf[2]
    compCap = conf[3]
    insight = conf[4]
    exp_eff = conf[5]
    pop_size = conf[6]
    mutation_prob = conf[7]
    crossover_prob = conf[8]
    number_of_gen = conf[9]
    alpha = conf[10]
    beta = conf[11]
    res = np.zeros(nTasks)
    genome_pos = genome[genome>0]
    res[genome_pos] = genome_pos*alpha+beta
    donate = np.zeros(nTasks)
    genome_neg = abs(genome[genome<0])
    donate[genome_neg] += res[genome_neg]*exp_eff
    res[genome_neg] -= res[genome_neg]*exp_eff
    return res,donate/8.

def grid_gtrad(grid,conf):
    n = conf[0]
    choice_of_u = conf[1]
    nTasks = conf[2]
    compCap = conf[3]
    insight = conf[4]
    exp_eff = conf[5]
    pop_size = conf[6]
    mutation_prob = conf[7]
    crossover_prob = conf[8]
    number_of_gen = conf[9]
    alpha = conf[10]
    beta = conf[11]
    res = np.zeros((n,n,nTasks))
    donate = np.zeros((n,n,nTasks))
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            res[i,j],donate[i,j] = genome_to_res_and_donate(grid[i,j],conf)
    return res,donate

def grid_sw(grid,conf):
    # Get resource vector for whole grid
    n = conf[0]
    choice_of_u = conf[1]
    nTasks = conf[2]
    compCap = conf[3]
    insight = conf[4]
    exp_eff = conf[5]
    pop_size = conf[6]
    mutation_prob = conf[7]
    crossover_prob = conf[8]
    number_of_gen = conf[9]
    alpha = conf[10]
    beta = conf[11]
    grid_res,grid_donate = grid_gtrad(grid,conf)
    #print grid_donate
    grid_donate = np.pad(grid_donate,((1,1),(1,1),(0,0)),'wrap')
    # grid_res_donated contains the unpacked result of grid_donate too be added to each agent's resource reservoir
    kernel = np.array([[1.,1.,1.],[1.,0.,1.],[1.,1.,1.]])
    kernel = kernel[:,:,None] 
    grid_donated = convolve(grid_donate,kernel,mode='valid')
    #print grid_donated 
    grid_res = grid_res + grid_donated  
    return np.sum(grid_uf(grid_res,conf))

def social_welfare(pop,conf):
    n = conf[0]
    choice_of_u = conf[1]
    nTasks = conf[2]
    compCap = conf[3]
    insight = conf[4]
    exp_eff = conf[5]
    pop_size = conf[6]
    mutation_prob = conf[7]
    crossover_prob = conf[8]
    number_of_gen = conf[9]
    alpha = conf[10]
    beta = conf[11]
    sw_ar = np.zeros(pop.shape[0])
    for i in range(pop.shape[0]):
        sw_ar[i] = grid_sw(pop[i],conf)
    return sw_ar

def crossover(parent1, parent2,conf):    
    n = conf[0]
    choice_of_u = conf[1]
    nTasks = conf[2]
    compCap = conf[3]
    insight = conf[4]
    exp_eff = conf[5]
    pop_size = conf[6]
    mutation_prob = conf[7]
    crossover_prob = conf[8]
    number_of_gen = conf[9]
    alpha = conf[10]
    beta = conf[11]
    rand1 = np.random.randint(n)
    rand2 = np.random.randint(n)
    rand3 = np.random.randint(compCap)

    temp = parent1[rand1,:rand2]

    temp_2 = parent2[rand1,:rand2]

    temp1 = list(parent1[rand1,rand2,:rand3])

    temp1_2 = list(parent2[rand1,rand2,:rand3])

    temp1 = temp1 + list(parent2[rand1,rand2,rand3:])

    temp1_2 = temp1_2 + list(parent1[rand1,rand2,rand3:])

    temp1 = np.asarray([temp1])

    temp1_2 = np.asarray([temp1_2])

    temp = np.append(temp, temp1, axis = 0)

    temp_2 = np.append(temp_2, temp1_2, axis = 0)

    temp2 = parent2[rand1, rand2+1:]

    temp2_2 = parent1[rand1, rand2+1:]

    temp = np.append(temp, temp2, axis = 0)

    temp_2 = np.append(temp_2, temp2_2, axis = 0)

    temp = np.asarray([temp])

    temp_2 = np.asarray([temp_2])

    grid1 = np.vstack((parent1[:rand1],temp,parent2[rand1+1:]))
    
    grid2 = np.vstack((parent2[:rand1],temp_2,parent1[rand1+1:]))
    
    return [grid1, grid2]

def mutate(toAppend,conf):
    n = conf[0]
    choice_of_u = conf[1]
    nTasks = conf[2]
    compCap = conf[3]
    insight = conf[4]
    exp_eff = conf[5]
    pop_size = conf[6]
    mutation_prob = conf[7]
    crossover_prob = conf[8]
    number_of_gen = conf[9]
    alpha = conf[10]
    beta = conf[11]
    
    a = np.random.rand(n,n,compCap)
    
    c = np.copy(toAppend)
    
    toMutate_ind = np.where(a < mutation_prob)
    
    c[toMutate_ind] = np.random.randint(low = -1*nTasks + 1, high  = nTasks, size = (c[toMutate_ind].shape))
    
    return c

def genetic_algorithm(population,conf):
    n = conf[0]
    choice_of_u = conf[1]
    nTasks = conf[2]
    compCap = conf[3]
    insight = conf[4]
    exp_eff = conf[5]
    pop_size = conf[6]
    mutation_prob = conf[7]
    crossover_prob = conf[8]
    number_of_gen = conf[9]
    alpha = conf[10]
    beta = conf[11]
    
    fitness_arr = np.asarray(social_welfare(population,conf)) #Returns numpy array of fitness
    
    inds = fitness_arr.argsort()[::-1] #Gives indices from max to min
    
    sortedPop = population[inds] #Sorts population based on fitness from highest to lowest
    
    fitness_arr[::-1].sort() #Sorts fitness array from max to min
    
    fitness_arr = fitness_arr/np.mean(fitness_arr) #Normalizes fitness for easier understansing
    
    prob_arr = fitness_arr / np.sum(fitness_arr)
    
    intermediate_ind = np.random.choice(len(prob_arr), pop_size, p=prob_arr)
    
    intermediates = population[intermediate_ind]
    
    temp = np.asarray(social_welfare(intermediates,conf))
    
    newpop = []
    
    newpop.append(sortedPop[0])
    newpop.append(sortedPop[1])
    parents_ind = np.random.choice(pop_size, pop_size)
        
    for i in range(2, pop_size, 2):

        parent1 = intermediates[parents_ind[i]]
        parent2 = intermediates[parents_ind[i+1]]

        x = np.random.rand()
    
        if x < crossover_prob:
            
            grids = crossover(parent1, parent2,conf)
            
            grid1 = grids[0]
            
            grid2 = grids[1]
            
            toAppend1 = grid1
            
            toAppend2 = grid2
            
            
        else:
            
            toAppend1 = parent1
            
            toAppend2 = parent2
            
        toAppend1 = mutate(toAppend1,conf)
        
        toAppend2 = mutate(toAppend2,conf)
        
        newpop.append(toAppend1)
            
        newpop.append(toAppend2)
            
    return np.asarray(newpop)

def DoRun(n, choice_of_u, nTasks, compCap, insight, exp_eff, pop_size, mutation_prob, crossover_prob, number_of_gen, alpha, beta,save_every):
    conf = [n,choice_of_u,nTasks,compCap,insight,exp_eff,pop_size,mutation_prob,crossover_prob,number_of_gen,alpha,beta]
    
    a = init_Pop(conf)
    b = genetic_algorithm(a,conf)
    #best_sw = []
    #best_grid = []

    
    # Create output folder and file
    if not os.path.exists('results'):
        os.makedirs('results')
    outfile = open("results/best_sw.csv","w+")
    outfile.write("generation,best_sw\n")

    for i in range(number_of_gen):
        #print i
        b = genetic_algorithm(b,conf)
        fitness_arr = np.asarray(social_welfare(b,conf)) #Returns numpy array of fitness
        inds = fitness_arr.argsort()[::-1] #Gives indices from max to min
        sortedPop = b[inds] #Sorts population based on fitness from highest to lowest
        outfile.write("%d,%f\n" % (i,fitness_arr.max()))
        if i%save_every==0:
            #print sortedPop[0]
            # Saves array in numpy readable format
            np.save("results/best_grid_"+str(i),sortedPop[0])
        #best_sw.append(fitness_arr.max())
        #best_grid.append(sortedPop[0])
    #return best_grid, best_sw


if __name__=="__main__":
    n = 3
    choice_of_u = 2
    nTasks = 10
    compCap = 10
    insight = 0.2
    exp_eff = 0.10

    pop_size = 100
    mutation_prob = 0.1
    crossover_prob = 0.75
    number_of_gen = 1000

    alpha = 3.
    beta = 5.

    save_every = 100

    DoRun(n,choice_of_u,nTasks,compCap,insight,exp_eff,pop_size,mutation_prob,crossover_prob,number_of_gen,alpha,beta,save_every)
