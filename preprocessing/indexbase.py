import json
import pandas as pd
import numpy as np
from functools import reduce
import os 
import multiprocessing
from multiprocessing import Pool,cpu_count

from tqdm import tqdm
import math

def indexbase(df,prefix): #Activity index base encoding ex) e1_a, e1_b, e2_d,e2_f...
    print('Start index base preprocessing.... \n')
    groups = df.groupby('Case ID')
    prefixlength =  prefix
    obj = {}
    case_name =[]

    for i in range(prefixlength):
        name = 'event'+str(i+1)
        obj[name]=[]

    length2 = len(set(df['Case ID']))
    for case,group in tqdm(groups):
        group = group.sort_values('Complete Timestamp').reset_index(drop=True)
        actlist = list(group['Activity'])
        case_name.append(case)
        for pos,act in enumerate(actlist):
            name = 'event'+str(pos+1)
            obj[name].append(act)
    dfk = pd.DataFrame(obj)
    columns = list(dfk.columns)
    concating=[]
    for col in columns:
        concating.append(pd.get_dummies(dfk[col],prefix=col))
    dfk = pd.concat(concating,axis=1)
    dfk['Case ID'] = case_name
    return dfk

def case_att_cat_onehot(df,columns): #Case attribute categorical column one hot encoding
    '''
    columns : list type object
    '''

    print('Start Case categorical attribute OHE preprocessing.... \n')
    groups = df.groupby('Case ID').first()
    concating =[]
    case =[]
    for col in columns:
        concating.append(pd.get_dummies(groups[col],prefix=col.capitalize()))
    dfk =pd.concat(concating,axis=1).reset_index(drop=True)
    dfk['Case ID'] = list(groups.index.values)
    return dfk

def case_att_con_onehot(df,columns): #Case attribute categorical column one hot encoding
    '''
    columns : list type object
    '''
    
    print('Start Case continuous attribute OHE preprocessing.... \n')
    groups = df.groupby('Case ID').first()
    concating=[]
    obj ={}
    for col in columns:
        print(col)
        toput = []
        for x in list(groups[col]):
            if math.isnan(x):
                pass
            else:
                toput.append(x)
        obj[col] = toput

        shortpoint = np.percentile(obj[col],100/3)

        midpoint = np.percentile(obj[col],200/3)
        obj2={}
        
        length2 = len(set(df['Case ID']))


        categorizedlist=[]
        targetcol = list(groups[col])
        for target in targetcol:
            if target < shortpoint:
                categorizedlist.append('Short')
            elif target >= shortpoint and target < midpoint:
                categorizedlist.append('Meidum')
            elif target >= midpoint:
                categorizedlist.append('Large')
            else:
                categorizedlist.append('Nan')

        groups[col] = categorizedlist
        dfk = pd.get_dummies(groups[col],prefix=col)
        if len(columns) ==1:
            pass
        else:
            concating.append(dfk)
    if len(columns) ==1:
        pass
    else:    
        dfk = pd.concat(concating,axis=1)
    # dfk['Case ID'] = list(df.groupby('Case ID').first().index.values)

    return dfk
    
def event_att_cat_onehot(df,columns,prefix):
    '''
    columns : list type object
    prefix : prefix length
    '''
    print('Start event categorical attribute OHE preprocessing.... \n')
    groups = df.groupby('Case ID')
    prefixlength =  prefix

    dropcol=[]
    for x in columns:
        if df[x].isnull().all():
            dropcol.append(x)
    columns = [x for x in columns if x not in dropcol]

    allconcating=[]
    for col in columns:
        print(col)
        obj = {}
        case_name =[]
        for i in range(prefixlength):
            name = str(col)+str(i+1)
            obj[name]=[]

        length2 = len(set(df['Case ID']))
       
        for case,group in tqdm(groups):
            group = group.sort_values('Complete Timestamp').reset_index(drop=True)
            actlist = list(group[col])
            case_name.append(case)
            for pos,act in enumerate(actlist):
                name = str(col)+str(pos+1)
                obj[name].append(act)

        dfk = pd.DataFrame(obj)
        columns = list(dfk.columns)
        concating=[]
        for col in columns:
            concating.append(pd.get_dummies(dfk[col],prefix=col))
        dfk = pd.concat(concating,axis=1)

        if len(columns) == 1:
            pass
        else:
            allconcating.append(dfk)
    if len(columns) ==1:
        pass
    else:
        dfk = pd.concat(allconcating,axis=1)
    
    dfk['Case ID'] = case_name
    return dfk


def event_att_con_onehot(df,columns,prefix): #Case attribute categorical column one hot encoding
    '''
    columns : list type object
    prefix : prefix length
    '''

    print('Start Event continuous attribute OHE preprocessing.... \n')
    groups = df.groupby('Case ID')
    concating =[]
    

    prefixlength =  prefix

    dropcol=[]
    for x in columns:
        if df[x].isnull().all():
            dropcol.append(x)
    columns = [x for x in columns if x not in dropcol]

    for col in columns:
        print(col)
        obj = {}
        for case, group in groups:
            event_attribute = list(group[col])
            for pos, att in enumerate(event_attribute):
                name = str(col).capitalize()+str(pos+1)
                if name not in list(obj.keys()):
                    obj[name] = [[att],1,{},[]]
                else:                
                    obj[name][0].append(att)
                    obj[name][1] +=1
        objkey = list(obj.keys())

        for key in obj.keys():
            obj[key][0] = [x for x in obj[key][0] if ~np.isnan(x)]
            obj[key][2]['Shortpoint'] = np.mean(obj[key][0])*0.4
            obj[key][2]['Midpoint'] = np.mean(obj[key][0])*0.6

        for case, group in groups:
            event_attribute = list(group[col])
            for pos, att in enumerate(event_attribute):
                name = str(col).capitalize()+str(pos+1)
                if name not in list(obj.keys()):
                    pass
                else:
                    shortpoint = obj[name][2]['Shortpoint']
                    midpoint  = obj[name][2]['Midpoint']
                    if att < shortpoint:
                        obj[name][3].append('Small')
                    elif att >= shortpoint and att < midpoint:
                        obj[name][3].append('Medium')
                    elif att > midpoint:
                        obj[name][3].append('Large')
                    else:
                        obj[name][3].append('Nan')

        obj2 ={x:obj[x][3] for x in obj.keys()}

        dfk = pd.DataFrame(obj2)
        columns2 = list(dfk.columns)
        concating2=[]
        for col in columns2:
            concating2.append(pd.get_dummies(dfk[col],prefix=col))
        dfk = pd.concat(concating2,axis=1)
        concating.append(dfk)
    
    
    dft = pd.concat(concating,axis=1)
    dft = dft.reset_index(drop=True)
    dft['Case ID'] = list(df.groupby('Case ID').first().index.values)
    return dft


def y_value(df,column):
    print('Start y value extraction preprocessing.... \n')
    m_dict={'Case ID':[],column:[]}
    df = df.rename(columns={column:'Label'})
    
    column = 'Label'
    groups = df.groupby('Case ID').first()
    
    m_dict['Case ID']=list(groups.index.values)
    m_dict[column] = list(groups[column])
    dfk = pd.DataFrame(m_dict,columns=['Case ID','Label'])
    
    dfk = pd.concat([dfk,pd.get_dummies(dfk['Label'],prefix=column)],axis=1)
    dfk = dfk.drop(column,axis=1)
    return dfk

def timediscretize(df,prefix): #3 cat, [short,medium,long] discretize
    print('Start time discretization preprocessing.... \n')
    df['Complete Timestamp'] =  pd.to_datetime(df['Complete Timestamp'])
    timeorder = {}
    groups = df.groupby('Case ID')

    length2 = len(set(df['Case ID']))

    for case,group in tqdm(groups):
        group = group.sort_values('Complete Timestamp').reset_index(drop=True)
        actlist = list(group['Activity'])
        length = len(group)
        timestamp =list(group['Complete Timestamp'])
        for pos, x in enumerate(actlist):
            if pos+1 != length:
                if ((x,actlist[pos+1])) not in list(timeorder.keys()):
                    timeorder[(x,actlist[pos+1])] =[[(timestamp[pos+1]- timestamp[pos]).total_seconds() / 60],1,{}]
                else:
                    timeorder[(x,actlist[pos+1])][0].append((timestamp[pos+1]- timestamp[pos]).total_seconds() / 60)
                    timeorder[(x,actlist[pos+1])][1] +=1

    for key in timeorder.keys():
        # timeorder[key][2]['Mean'] = np.mean(timeorder[key][0])
        timeorder[key][2]['Shortpoint'] = np.percentile(timeorder[key][0],100/3)
        timeorder[key][2]['Midpoint'] = np.percentile(timeorder[key][0],200/3) 

    prefixlength =  prefix
    obj = {}
    case_name =[]
    for i in range(prefixlength-1):
        name = 'Time'+str(i+1)
        obj[name]=[]

    length2 = len(set(df['Case ID']))

    for case,group in groups:
        group = group.sort_values('Complete Timestamp').reset_index(drop=True)
        actlist = list(group['Activity'])
        case_name.append(case)
        timestamp =list(group['Complete Timestamp'])
        for pos,x in enumerate(actlist):
            if pos+1 != length:
                actpair = ((x,actlist[pos+1]))
                timedifference = (timestamp[pos] - timestamp[pos-1]).total_seconds() /60
                shortpoint = timeorder[actpair][2]['Shortpoint']
                midpoint = timeorder[actpair][2]['Midpoint']
                name = 'Time'+str(pos+1)
                if timedifference < shortpoint:
                    obj[name].append('Short')
                elif timedifference >= shortpoint and timedifference < midpoint:
                    obj[name].append('Medium')
                elif timedifference >= midpoint:
                    obj[name].append('Long')
                else:
                    obj[name].append('all0')
            
    dfk = pd.DataFrame(obj)
    columns = list(dfk.columns)
    concating=[]
    for col in columns:
        concating.append(pd.get_dummies(dfk[col],prefix=col))
    dfk = pd.concat(concating,axis=1)
    dfk['Case ID'] = case_name    
    
    return dfk


def timediscretize2(df,prefix):
    print('Start time discretization preprocessing.... \n')
    df['Start Timestamp'] =  pd.to_datetime(df['Start Timestamp'])
    df['Complete Timestamp'] =  pd.to_datetime(df['Complete Timestamp'])
    timeorder = {}
    groups = df.groupby('Activity')

    for act, group in groups:
        duration = list(group['Complete Timestamp']-group['Start Timestamp'])
        nduration=[]
        for dur in duration:
            nduration.append((dur.total_seconds() / 60))
        timeorder[act] = [np.mean(nduration),np.percentile(nduration,100/3),np.percentile(nduration,200/3)]
    
    groups = df.groupby('Case ID')

    concating=[]

    obj = {}
    case_name =[]
    for i in range(prefix):
        name = 'Time'+str(i+1)
        obj[name]=[]

    length2 = len(set(df['Case ID']))
    for case, group in groups:
        group = group.reset_index(drop=True).sort_values(by='Start Timestamp')
        actlist = list(group['Activity'])
        duration = list(group['Complete Timestamp']-group['Start Timestamp'])
        timelist=[]
        for dur in duration:
            timelist.append((dur.total_seconds() / 60))

        for pos,time in enumerate(timelist):
            act = actlist[pos]
            if timeorder[act][0] == timeorder[act][1] == timeorder[act][2]:
                obj['Time'+str(pos+1)].append('all0')
            else:
                if time < timeorder[act][1]:
                    obj['Time'+str(pos+1)].append('Short')
                elif time >= timeorder[act][1] and time < timeorder[act][2]:
                    obj['Time'+str(pos+1)].append('Middle')
                elif time >= timeorder[act][2]:
                    obj['Time'+str(pos+1)].append('Long')
                else:
                    obj['Time'+str(pos+1)].append('all0')


    dfk = pd.DataFrame(obj)
    columns = list(dfk.columns)
    for col in columns:
        concating.append(pd.get_dummies(dfk[col],prefix=col))
    dfk = pd.concat(concating,axis=1)
    dfk['Case ID'] = list(df.groupby('Case ID').first().index.values)
    return dfk
    

def variance(df,prefix):
    variant=[]
    
    groups = df.groupby('Case ID')
    concating={}
    for case, group in groups:
        group = group.sort_values('Start Timestamp').reset_index(drop=True)
        trace = list(group['Activity'])
        if trace not in variant:
            variant.append(trace)
        # group['Variance'] = variant.index(trace)+1
        concating[case] = variant.index(trace)+1
    
    
    dfk = pd.Series(concating).reset_index(drop=False)
    dfk = dfk.rename(columns={'index':'Case ID',0:'Variance'})
    caseid = list(dfk['Case ID'])
    dfk = pd.get_dummies(dfk['Variance'],prefix='Variance')
    dfk['Case ID'] = caseid

    variantdic={}
    for pos,trace in enumerate(variant):
        variantdic[pos+1] = trace
    dft = pd.Series(variantdic).reset_index(drop=False)
    dft = dft.rename(columns={'index':'Variance',0:'Trace'})
    
    dft.to_json('./production/indexbase/prefix'+str(prefix)+'/variance_base/Variance_trace.json',orient='records')
    return dfk


if __name__=='__main__':


    for k in range(5,6):
        prefix = k
        print('Prefix length : %s'%(prefix))

        # dirname = '../sepsis/rule1/prefix'+str(prefix)
        # df = pd.read_csv(dirname+'/Sepsis Cases_prep.csv')
        df = pd.read_csv('../data/bpic2011prep.csv')
        print(df.columns.values)
        
    #     case_att_cat = ['Diagnose','DiagnosticArtAstrup','DiagnosticBlood','DiagnosticECG','DiagnosticIC','DiagnosticLacticAcid',
    #                     'DiagnosticLiquor','DiagnosticOther','DiagnosticSputum','DiagnosticUrinaryCulture','DiagnosticUrinarySediment',
    #                     'DiagnosticXthorax','DisfuncOrg','Hypotensie','Hypoxie','InfectionSuspected','Infusion','Oligurie','SIRSCritHeartRate',
    #                     'SIRSCritLeucos','SIRSCritTachypnea','SIRSCritTemperature','SIRSCriteria2OrMore']
    #     case_att_con = ['Age']
    #     event_att_cat = ['Activity','Resource']
    #     event_att_con = ['CRP','LacticAcid','Leucocytes']

        
    #     savedir = '../sepsis/rule1/indexbase/prefix'+str(prefix)+'/simple_timediscretize'
        
    #     try:
    #         os.makedirs(savedir)
    #     except:
    #         pass        
        
    #     y_column = 'label'

    #     dfs = [event_att_con_onehot(df,event_att_con,prefix),timediscretize(df,prefix),y_value(df,y_column),event_att_cat_onehot(df,event_att_cat,prefix),
    #     case_att_cat_onehot(df,case_att_cat),case_att_con_onehot(df,case_att_con)]

    #     df_final = reduce(lambda  left,right: pd.merge(left,right,on='Case ID'),dfs)
        

    #     df_final.to_csv(savedir+'/ARMinput_preprocessed.csv',index=False)
    

    # playsound('../Yattong edited version.mp3')







