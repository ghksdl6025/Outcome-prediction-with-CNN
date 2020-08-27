import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import math
from sklearn import preprocessing
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)



def case_att_cat(df,columns): #Case attribute categorical column one hot encoding
    '''
    columns : list type object
    '''

    print('Start Case categorical attribute OHE preprocessing.... \n')
    groups = df.groupby('Case ID')
    concating =[]
    for _,group in groups:
        for col in columns:
            group.loc[0,col] = set(group[col]).pop()
        concating.append(group)
    df = pd.concat(concating).reset_index(drop=True)    
    groups = df.groupby('Case ID').first()
    concating=[]
    for col in columns:
        concating.append(pd.get_dummies(groups[col],prefix=col.capitalize()))
    dfk =pd.concat(concating,axis=1).reset_index(drop=True)
    return dfk

def case_att_con(df,columns): #Case attribute continuous columns
    '''
    Get the continuous value of given columns by cases and standardize
    columns : list type object
    '''
    print('Start Case continuous attribute concatanating.... \n')
    groups = df.groupby('Case ID')
    concating =[]
    for _,group in groups:
        for col in columns:
            group.loc[0,col] = set(group[col]).pop()
        concating.append(group)
    df = pd.concat(concating).reset_index(drop=True)    

    groups = df.groupby('Case ID').first()
    concating=[]
    for col in columns:
        groups[col] = preprocessing.scale(groups[col])
        concating.append(groups[col])
    dfk = pd.concat(concating,axis=1).reset_index(drop=True)
    return dfk

def event_att_cat(df,columns): #Case attribute categorical columns
    '''
    columns : list type object
    '''
    print('Start Event categorical attribute concatanating.... \n')
    df = df.loc[:,['Case ID']+columns]
    groups = df.groupby('Case ID')
    concating2=[]

    for _,group in groups:
        prefixlength = len(group)
        concating=[]
        for col in columns:
            group_col = group.loc[:,col]
            indexlist = [str(col)+'_'+str(x+1) for x in range(prefixlength)]
            group_col.index = indexlist
            concating.append(group_col.to_frame().T.reset_index(drop=True))
        concating2.append(pd.concat(concating,axis=1))            
    dfk = pd.concat(concating2).reset_index(drop=True)

    concatingall=[]
    for col in list(dfk.columns.values):
        concatingall.append(pd.get_dummies(dfk[col],prefix=col))
    return pd.concat(concatingall,axis=1).reset_index(drop=True)



def event_att_con(df,columns): #Event attribute continuous columns
    '''
    columns : list type object
    '''
    print('Start Event continuous attribute concatanating.... \n')
    df = df.loc[:,['Case ID']+columns]
    groups = df.groupby('Case ID')
    concating2=[]
    for _, group in groups:
        prefixlength = len(group)
        concating=[]
        for col in columns:
            group_col = group.loc[:,col]
            indexlist = [str(col)+'_'+str(x+1) for x in range(prefixlength)]
            group_col.index = indexlist
            concating.append(group_col.to_frame().T.reset_index(drop=True))
        concating2.append(pd.concat(concating,axis=1))
    dft = pd.concat(concating2).reset_index(drop=True)
    for col in list(dft.columns.values):
        dft[col] = preprocessing.scale(dft[col])
    return dft

# Transform timestamp to get month,weekday, hour, duration from previous event, duration from start, position of the event
# Categorical attributes, month, weekday, and hour are converted into one hot encoded dataframe
# Weekday 0 as monday to 6 as Sunday
# Duration is written in total_minutes
# Two duration related values and position are recorded in 'as is'.
def time_pre(df,prefixlength):
    df['Complete Timestamp'] =pd.to_datetime(df['Complete Timestamp'])
    df = df.sort_values(by='Complete Timestamp')
    groups = df.groupby('Case ID')

    timedf =[]
    for _, group in groups:
        timelist= list(group['Complete Timestamp'])
        ngroup = pd.DataFrame()
        for pos,t in enumerate(timelist):
            ngroup.loc[pos,'Timemonth'] =t.month
            ngroup.loc[pos,'Timeweekday'] =t.isoweekday()
            ngroup.loc[pos,'Timehour'] =t.hour

            first_time = timelist[0]
            target_time = timelist[pos]
            if pos == 0:
                pre_target_time = timelist[pos]
            else:
                pre_target_time = timelist[pos-1]

            duration_from_pre = target_time - pre_target_time
            duration_from_first = target_time - first_time

            ngroup.loc[pos,'Duration'] =duration_from_pre.total_seconds() / 60.0
            ngroup.loc[pos,'Cumduration'] =duration_from_first.total_seconds() / 60.0


        timedf.append(ngroup)
    timedf = pd.concat(timedf).reset_index(drop=True)
    return timedf


    
if __name__=='__main__':
    dft = pd.read_csv('../data/BPIC2011_prefix5.csv')

    agelist = list(dft['(case) Age'])
    nagelist=[]
    for age in agelist:
        if math.isnan(age):
            nagelist.append(0)
        else:
            nagelist.append(age)
    dft['(case) Age'] = nagelist
    
    dft = pd.concat([dft,time_pre(dft,5)],axis=1)

    case_cat =['(case) Diagnosis code', '(case) Diagnosis code:1',
        '(case) Diagnosis code:10', '(case) Diagnosis code:11', '(case) Diagnosis code:12',
        '(case) Diagnosis code:13', '(case) Diagnosis code:14', '(case) Diagnosis code:15',
        '(case) Diagnosis code:2', '(case) Diagnosis code:3', '(case) Diagnosis code:4',
        '(case) Diagnosis code:5', '(case) Diagnosis code:6', '(case) Diagnosis code:7', '(case) Diagnosis code:8',
        '(case) Diagnosis code:9', '(case) Specialism code', '(case) Specialism code:1', '(case) Specialism code:10',
        '(case) Specialism code:11', '(case) Specialism code:12', '(case) Specialism code:13',
        '(case) Specialism code:14', '(case) Specialism code:15', '(case) Specialism code:2',
        '(case) Specialism code:3', '(case) Specialism code:4', '(case) Specialism code:5',
        '(case) Specialism code:6', '(case) Specialism code:7', '(case) Specialism code:8',
        '(case) Specialism code:9', '(case) Treatment code', '(case) Treatment code:1',
        '(case) Treatment code:10', '(case) Treatment code:11', '(case) Treatment code:12',
        '(case) Treatment code:13', '(case) Treatment code:14', '(case) Treatment code:15',
        '(case) Treatment code:2', '(case) Treatment code:3', '(case) Treatment code:4',
        '(case) Treatment code:5', '(case) Treatment code:6', '(case) Treatment code:7',
        '(case) Treatment code:8', '(case) Treatment code:9',]
    case_con =['(case) Age']
    event_cat =['Activity','Section','Specialism code','Producer code','org:group','Timemonth','Timeweekday','Timehour']
    event_con =['Duration','Cumduration']
    cols = ['Case ID', 'Label']

    caseid = dft.groupby('Case ID')
    caseidlist = []
    labellist = []
    for case, group in caseid:
        
        caseidlist.append(case)
        labellist.append(set(group['Label']).pop())
    print(len(caseidlist))
    print(len(labellist))

    dfk = pd.concat([case_att_cat(dft,case_cat),case_att_con(dft,case_con),event_att_con(dft,event_con),event_att_cat(dft,event_cat)],axis=1)
    print(dfk.shape)
    dfk['Case ID'] = caseidlist
    dfk['Label'] = labellist
    dfk.to_csv('../data/bpic2011/indexbase_prefix5.csv',index=False)