#
# Author: Henrique Pereira Coutada Miranda
# Run a GW calculation using Yambo
#
from __future__ import print_function
import sys
from yambopy import *
from qepy import *
import argparse

#parse options
parser = argparse.ArgumentParser(description='GW convergence')
parser.add_argument('-r' ,'--run',  action="store_true", help='Run the calculation')
parser.add_argument('-p' ,'--plot', action="store_true", help='Pack into json files and plot the results')
args = parser.parse_args()

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

yambo = 'yambo'
prefix = 'si'

if not os.path.isdir('database'):
    os.mkdir('database')

#check if the nscf cycle is present
if os.path.isdir('nscf/%s.save'%prefix):
    print('nscf calculation found!')
else:
    print('nscf calculation not found!')
    exit() 

#check if the SAVE folder is present
if not os.path.isdir('database/SAVE'):
    print('preparing yambo database')
    os.system('cd nscf/%s.save; p2y'%prefix)
    os.system('cd nscf/%s.save; yambo'%prefix)
    os.system('mv nscf/%s.save/SAVE database'%prefix)

if not os.path.isdir('gw_conv'):
    os.mkdir('gw_conv')
    os.system('cp -r database/SAVE gw_conv')

if args.run:
    #create the yambo input file
    y = YamboIn('%s -p p -g n -V all'%yambo,folder='gw_conv')
    y['GbndRnge'] = [[1,15],'']
    y['QPkrange'][0][2:4] = [2,6]
    conv = { 'FFTGvecs': [[5,10,15],'Ry'],
             'NGsBlkXp': [[1,2,3], 'Ry'],
             'BndsRnXp': [[1,10],[1,20],[1,30]] }

    def run(filename):
        """ Function to be called by the optimize function """
        folder = filename.split('.')[0]
        print(filename,folder)
        os.system('cd gw_conv; yambo -F %s -J %s -C %s 2> %s.log'%(filename,folder,folder,folder))

    y.optimize(conv,run=run)

if args.plot:
    #pack the files in .json files
    pack_files_in_folder('gw_conv')

    #plot the results using yambm analyser
    ya = YamboAnalyser('gw_conv')
    print(ya)
    print('plot all qpoints')
    ya.plot_gw('qp')
    print('plot along a path')

    path = [[[0.5,   0,   0],'L'],
            [[  0,   0,   0],'$\Gamma$'],
            [[  0, 0.5, 0.5],'X'],
            [[1.0, 1.0, 1.0],'$\Gamma$']]
    ya.plot_gw_path('qp',path)

    print('done!')
