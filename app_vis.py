import pandas as pd
import folium
import os
import time
from folium import FeatureGroup, LayerControl,Map,Marker,plugins
import glob
print('enter year1 multiplier')
mul_year1=float(input())
print('enter year2 multiplier')
mul_year2=float(input())
filenames = glob.glob(os.getcwd() + "/path/*/AVA_RSLTE001_LNCELL_DAILY_PROCESS.csv")
li=[]
for filename in filenames:
    df = pd.read_csv(filename, delimiter=';',encoding='latin1')
    print('reading data')
    li.append(df)
data=li
print('number of days:',len(data))
print('reading capacity growth file')
solution=pd.read_csv('cap_grow.csv',encoding = "ISO-8859-1")
sol_file=[]
for i in range(len(data)):
    print('creating solutions')
    split=pd.DataFrame()
    split['PERIOD_START_TIME']=data[i]['PERIOD_START_TIME']
    split['MRBTS_SBTS_name']=data[i]['MRBTS_SBTS_name']
    split['LNCEL_name']=data[i]['LNCEL_name']
    split['PDCP_SDU_Volume_DL']=data[i]['PDCP_SDU_Volume_DL']
    split['PDCP_SDU_Volume_UL']=data[i]['PDCP_SDU_Volume_UL']
    input_file=pd.read_excel('Cutomer input sheet.xlsx')
    df_left = pd.merge(split, input_file, on=['LNCEL_name','MRBTS_SBTS_name'], how='left')
    df_left['total_payload']=(df_left['PDCP_SDU_Volume_DL']+df_left['PDCP_SDU_Volume_UL'])/1024
    frame2=pd.DataFrame(df_left,columns=['PERIOD_START_TIME','Lat','Long','MRBTS_SBTS_name','LNCEL_name','Site id','total_payload'])
    frame2.rename(columns={'total_payload':'Y0'},inplace=True)
    frame2['solution_site_Y0']=' '
    frame2['Y1']=mul_year1*frame2['Y0']
    frame2['solution_sector']=' '
    frame2['solution_site']=' '
    frame2['Y2']=mul_year2*frame2['Y0']
    frame2['solution_sector_Y2']=' '
    frame2['solution_site_Y2']=' '
    for i in range(len(solution)):
                if(solution['type'].iloc[i]=='sector'):
                    if(solution['year1'].iloc[i]!='0'):
                        sol_range=list(map(int,(solution['year1'].iloc[i]).split('-')))
                        sol2_range=list(map(int,(solution['year2'].iloc[i]).split('-')))
                        low2=sol2_range[0]

                        low=sol_range[0]
                        if(len(sol2_range)==2):
                            high2=sol2_range[1]
                            frame2.loc[(frame2['Y2']>low2) & (frame2['Y2']<high2),"solution_sector_Y2"]=solution['Solution'].iloc[i]
                        if(len(sol_range)==1):
                            frame2.loc[(frame2['Y2']>low2),"solution_sector_Y2"]=solution['Solution'].iloc[i]

                        if(len(sol_range)==2):
                            high=sol_range[1]
                            
                            frame2.loc[(frame2['Y1']>low) & (frame2['Y1']<high),"solution_sector"]=solution['Solution'].iloc[i]
                            frame2.loc[(frame2['Y0']>low) & (frame2['Y0']<high),"solution_sector_Y0"]=solution['Solution'].iloc[i]

                        if(len(sol_range)==1):
                            frame2.loc[(frame2['Y1']>=low),"Y0"]=solution['Solution'].iloc[i]
                            #frame2.loc[(frame2['Y0']>low),"solution_sector_Y0"]=solution['Solution'].iloc[i]
    sol_file.append(frame2)
    frame=pd.concat(sol_file,ignore_index=True)
new=frame
m=new.groupby('MRBTS_SBTS_name')
new.set_index('MRBTS_SBTS_name',inplace=True)
for i in range(len(solution)):
    if(solution['type'].iloc[i]=='site'):
        if(solution['year1'].iloc[i]!='0'):
            sol_range=list(map(int,(solution['year1'].iloc[i]).split('-')))
            sol2_range=list(map(int,(solution['year2'].iloc[i]).split('-')))
            low=sol_range[0]
            low2=sol2_range[0]

    for name,group in m :
        if(len(sol_range)==2):
            
            high=sol_range[1]
            high2=sol2_range[1]
            if((group.Y1>=low).all() and (group.Y1<=high).all()):
                print(group)
                new.loc[[name],'solution_site']=solution['Solution'].iloc[i]
                            
            if((group.Y2>=low2).all() and (group.Y2<=high2).all()):
                new.loc[[name],'solution_site_Y2']=solution['Solution'].iloc[i]
                print(group)
            #if((group.Y0>=low).all() and (group.Y0<=high).all()):
                #new.loc[[name],'solution_site_Y0']=solution['Solution'].iloc[i]
                                    
        if(len(sol_range)==1):
            
            if((group.Y1>=low).all()):
                print(group)
                new.loc[[name],'solution_site']=solution['Solution'].iloc[i]
            if((group.Y2>=low2).all()):
                new.loc[[name],'solution_site_Y2']=solution['Solution'].iloc[i]
                
            #if((group.Y0>=low2).all()):
                #new.loc[[name],'solution_site_Y0']=solution['Solution'].iloc[i]
new.to_csv('final.csv')

maindf=pd.read_csv("final.csv")#here the data which is given by you
maindf['Lat'] = maindf['Lat'].str.replace(',', '')#latitude column conatins baddata so data cleaning is done 
maindf=maindf[pd.notnull(maindf['Lat'])]#na values are present in latitude so we removed that
maindf=maindf[pd.notnull(maindf['Long'])]#na values are present in longitude so we removed that
maindf=maindf.reset_index()#the index is reseted
firstLat=float(maindf['Lat'][0])#for map center we have taken first point
firstLong=float(maindf['Long'][0])
test_list=list(maindf['solution_sector_Y2'].unique())#to see how many solutions are there in that row
maindf=maindf.drop(['index'], axis=1)
while(" " in test_list) : 
    test_list.remove(" ")#there is blank in the test list above so to remove that we used this sentence
nrml_list=test_list.copy()



while(True):
    print(maindf['PERIOD_START_TIME'].unique())
    print('Enter date. Type exit to close')
    date=str(input())
    if(date=='exit'):
        break
    dateofsite=date#select the date of site here

    print('creating visualization. Please Wait...')

    df=maindf[maindf['PERIOD_START_TIME']==dateofsite]#getting the data in that dateofsite
    m = folium.Map(location=[firstLat, firstLong], zoom_start=6, tiles=None)#map with custom name of tile 
    folium.TileLayer('openstreetmap', name='Sitewise solutions').add_to(m)

    colouricon=['red', 'blue', 'green', 'purple', 'orange', 'darkred',
             'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
             'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen',
             'gray', 'black', 'lightgray']# colours of the icons inside that



    mcgg = folium.plugins.MarkerCluster(control=False)#making marker cluster for year0
    m.add_child(mcgg)
    fg = folium.plugins.FeatureGroupSubGroup(mcgg,name='Year - 0')#naming this will appear on the map
    m.add_child(fg)
    kk=list(zip(df.Lat, df.Long))#to add the latitude and longitude to the marker 
    for i in range(len(df['Lat'])):
        folium.Marker(kk[i],popup=["MRBTS ID = ",df['MRBTS_SBTS_name'].iloc[i],"LNCEL_name = ",df['LNCEL_name'].iloc[i],"latlong = ",kk[i],"solution=",df['Y0'].iloc[i]],icon=folium.Icon(color=colouricon[-1], icon='ok-sign')).add_to(fg)  


    mcggg = folium.plugins.MarkerCluster(control=False)
    m.add_child(mcggg)
    fgg = folium.plugins.FeatureGroupSubGroup(mcggg,name='Year - 1',show=False)
    m.add_child(fgg)
    for i in range(len(df['Lat'])):
        folium.Marker(kk[i],popup=["MRBTS ID = ",df['MRBTS_SBTS_name'].iloc[i],"LNCEL_name = ",df['LNCEL_name'].iloc[i],"latlong = ",kk[i],"solution=",df['Y1'].iloc[i]],icon=folium.Icon(color=colouricon[-2], icon='ok-sign')).add_to(fgg)  




    mcg = folium.plugins.MarkerCluster(name='solution_sector_Y2',control=True,show=False)
    m.add_child(mcg)
    lgd_txt = '<span style="color: {col};">{txt}</span>'#legends are colour based so as to easily identify the sectorsite solution
    for i in range(len(nrml_list)):
        nrml_list[i] = folium.plugins.FeatureGroupSubGroup(mcg,name= lgd_txt.format( txt= test_list[i], col= colouricon[i]))
        m.add_child(nrml_list[i])


    for i in range(len(nrml_list)):
        ddd=df[df['solution_sector_Y2']==test_list[i]]
        ddd.reset_index()
        dd=list(zip(ddd.Lat, ddd.Long))
        for j in range(len(dd)):
            folium.Marker(dd[j],popup=["MRBTS ID = ",ddd['MRBTS_SBTS_name'].iloc[j],"latlong = ",dd[j]],icon=folium.Icon(color=colouricon[i], icon='ok-sign')).add_to(nrml_list[i])  

    folium.LayerControl(collapsed=False).add_to(m)
    m.save('vis_'+date+'.html')#here u will get the output in html format in less than 60 sec
    
print('done')