import pandas as pd
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Categorical attributes to One hot encoding
def cat_pre(df, last_state, cat_att):
    df = df.sort_values(by='Complete Timestamp')
    last_state = last_state -1

    groups = df.groupby('Case ID').apply(lambda x: x.iloc[last_state,:]) 
    dfn = groups.loc[:,cat_att].reset_index()

    ohe_df=[]
    for att in cat_att:
    
        processed = pd.get_dummies(dfn[att],prefix=str(att))
        ohe_df.append(processed)
    
    dft = pd.concat(ohe_df,axis=1)
    return dft

# Select last_state of each cases
def con_pre(df,last_state,con_att):
    df = df.sort_values(by='Complete Timestamp')
    last_state = last_state -1

    groups = df.groupby('Case ID').apply(lambda x: x.iloc[last_state,:]) 
    groups = groups.loc[:,con_att]
    dfn = groups.reset_index()
    return dfn

# Transform timestamp to get month,weekday, hour, duration from previous event, duration from start, position of the event
# Categorical attributes, month, weekday, and hour are converted into one hot encoded dataframe
# Weekday 0 as monday to 6 as sunday
# Two duration related values and position are recorded in 'as is'.
def time_pre(df,last_state):
    df['Complete Timestamp'] =pd.to_datetime(df['Complete Timestamp'])
    df = df.sort_values(by='Complete Timestamp')
    last_state = last_state -1
    groups = df.groupby('Case ID').apply(lambda x: x.iloc[last_state,:]) 

    timelist= list(groups['Complete Timestamp'])
    monthlist=[]
    weekdaylist= []
    hourlist=[]
    for t in timelist:
        monthlist.append(t.month)
        weekdaylist.append(t.isoweekday())
        hourlist.append(t.hour)
    
    duration_previous=[]
    duration_first=[]
    groups = df.groupby('Case ID')
    for _, group in groups:
        timelist = list(group['Complete Timestamp'])
        target_time = timelist[last_state-1]
        pre_target_time = timelist[last_state-2]
        firs_time = timelist[0]
        duration_from_pre = target_time - pre_target_time
        duration_from_first = target_time - firs_time
        duration_previous.append(duration_from_pre.total_seconds())
        duration_first.append(duration_from_first.total_seconds())
    
    dfk = pd.DataFrame(columns=['Time_month','Time_hour','Time_weekday','Duration from previous','Duration from start'])
    dfk['Time_month'] = monthlist
    dfk['Time_hour'] = hourlist
    dfk['Time_weekday'] = weekdaylist
    dfk['Duration from previous'] = duration_previous
    dfk['Duration from start'] = duration_first


    for att in ['Time_month','Time_hour','Time_weekday']:
        ohe_time=pd.get_dummies(dfk[att],prefix=str(att))
        dfk = dfk.drop(att,axis=1)
        dfk = pd.concat([dfk,ohe_time],axis=1)

    return dfk 
    
# Target outcome label
def label_add(df,last_state):
    df['Complete Timestamp'] =pd.to_datetime(df['Complete Timestamp'])
    df = df.sort_values(by='Complete Timestamp')
    last_state = last_state -1
    groups = df.groupby('Case ID').apply(lambda x: x.iloc[last_state,:]) 
    
    # groups = pd.get_dummies(groups['Label'],prefix='Label')
    groups = groups.loc[:,'Label']
    groups = groups.reset_index(drop=True)
    
    return groups
    


if __name__ =='__main__':

    last_state = 5
    df = pd.read_csv('../data/BPIC2015_2prep_prefix5.csv')
    ['Case ID' 'Complete Timestamp'  'Label']

    #Neglect '(case) case_type','lifecycle:transition' attributes, single value across all cases
    #Neglect planned dueDate dateStop dateFinished activityNameEN activityNameNL concept:name

    event_cat_att = ['Activity','Resource','action_code','question']
    event_con_att = []
    case_cat_att =['(case) IDofConceptCase','(case) Includes_subCases','(case) Responsible_actor','(case) caseProcedure','(case) caseStatus','(case) last_phase',
                    '(case) parts','(case) requestComplete','(case) termName','(case) landRegisterID','monitoringResource']
    case_con_att=['(case) SUMleges',]

    cat_att = event_cat_att + case_cat_att
    con_att = event_con_att + case_con_att

    cat = cat_pre(df, last_state,cat_att)
    con = con_pre(df,last_state,con_att)
    time = time_pre(df,last_state)
    label = label_add(df,last_state)

    pre_processed_input = pd.concat([cat,con,time,label],axis=1)

    preprocessed_name = 'last_state_' + str(last_state)+'.csv' 
    pre_processed_input.to_csv('../data/'+preprocessed_name,index=False)


