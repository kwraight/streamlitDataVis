### standard
import streamlit as st
from core.Page import Page
### custom
import pandas as pd
import altair as alt
from faker import Faker
from random import uniform, choice, randint
import ast
import csv
import copy
### PDB stuff
import core.stInfrastructure as infra
import commonCode.StreamlitTricks as stTrx


#####################
### useful functions
#####################

def GetChart(df_data,chartType):
    if chartType=="bar":
        return alt.Chart(df_data).mark_bar()
    elif chartType=="scatter":
        return alt.Chart(df_data).mark_point()
    elif chartType=="line":
        return alt.Chart(df_data).mark_line()
    elif chartType=="area":
        return alt.Chart(df_data).mark_area()
    elif chartType=="rect":
        return alt.Chart(df_data).mark_rect()
    elif chartType=="tick":
        return alt.Chart(df_data).mark_tick()

    else:
        st.write("Don't know what to do with",pageDict['properties']['chartType'])
    return None

def GenerateData(properties,dataList):
    dataSet=[]
    # st.write(dataList)
    for x in range(0,properties['population'],1):
        valDict={}
        for dl in dataList:
            if dl['dataType']=="quantity":
                valDict[dl['name']]=uniform(dl['domain'][0],dl['domain'][1])
            elif dl['dataType']=="quality":
                valDict[dl['name']]=choice(dl['domain'])#dl['domain'][randint(0, len(dl['domain']-1))]#
            else:
                st.write("Don't know what to do with",dl['dataType'])
        dataSet.append(valDict)
    return dataSet

infoList=["### Instructions",
        " __NB__ Currently only supporting [_Altair_](https://altair-viz.github.io)",
        "  1. Select _chart type_ and _population_ (number of entries)",
        "  2. Input _channels_ (types of information) - _X_ & _Y_ required",
        "  3. Generate data (based on _channel_ inputs)",
        "  4. Plot data"]
#####################
### main part
#####################

class Page1(Page):
    def __init__(self):
        super().__init__("DataViser", ":microscope: Data Visualisation Tester", infoList)

    def main(self):
        super().main()

        ### getting attribute
        pageDict=st.session_state[self.name]

        [st.write(x) for x in infoList]

        ### set up lists
        popList=[1,10,100,1000]
        dataTypeList=['quantity','quality']
        dataTypeMap={'quantity':"Q",'quality':"N"}

        ### set up defaults
        defDict={'faker':Faker(),'population':100,'chartType':"scatter"}
        stTrx.DebugOutput("Defaults",defDict)
        if 'properties' not in pageDict.keys():
            pageDict['properties']= copy.deepcopy(defDict)


        ### selections
        st.write("## 1. Basic Properties")

        chartTypeList=['bar','scatter','line','area','rect','tick']
        infra.SelectBox(pageDict['properties'],'chartType',chartTypeList,"Select chart Type")

        infra.SelectBox(pageDict['properties'],'population',popList,"Select population")


        ### axes
        st.write("### 2. Define Channels")
        if 'axes' not in pageDict.keys():
            pageDict['axes']=[]
        infra.ToggleButton(pageDict,'togDefAxis','Define Axis?')
        if pageDict['togDefAxis']:
            axisDictOpts={'axisType':['X','Y','colour','shape','opacity'],'name':"SetName",'dataType':dataTypeList}
            axisDict={}
            for k,v in axisDictOpts.items():
                if type(v)==type([]):
                    infra.SelectBox(axisDict,k,v,k)
                if type(v)==type({}):
                    infra.SelectBox(axisDict,k,v,k,'name')
                elif type(v)==type("string"):
                    axisDict[k]=v+"_"+axisDict['axisType']
                    infra.TextBox(axisDict,k,k)
                else:
                    st.write("Don't know what to do with",k)
            if axisDict['dataType']=="quantity":
                vLo=st.selectbox('minimum value',[x*10 for x in range(0,10,1)])
                vHi=st.selectbox('maximum value',[x*10 for x in range(1,11,1)])
                axisDict['domain']=[int(vLo),int(vHi)]
            elif axisDict['dataType']=="quality":
                cats=st.selectbox('number of categories',[x for x in range(1,11,1)])
                axisDict['domain']=[pageDict['properties']['faker'].first_name() for x in range(0,cats,1)]
            else:
                st.write("Don't know what to do with",axisDict['dataType'])

            stTrx.DebugOutput("axisDict:",pageDict['axes'])
            if st.button("Add axis?"):
                if axisDict['axisType'] in [x['axisType'] for x in pageDict['axes']]:
                    pageDict['axes'].remove(next(item for item in pageDict['axes'] if item['axisType'] == axisDict['axisType']))
                pageDict['axes'].append(axisDict)

        for a in ['X','Y']:
            if a not in [x['axisType'] for x in pageDict['axes']]:
                st.write("no",a,"axis defined")
                st.stop()

        stTrx.DebugOutput("axisDict:",pageDict['axes'])

        infra.ToggleButton(pageDict,'togDrop',"Drop axis?")
        if pageDict['togDrop']:
            axNameList=[x['name'] for x in pageDict['axes']]
            dropName=st.selectbox("Select axis to drop:",axNameList)
            if st.button("drop "+dropName):
                pageDict['axes'].remove(next(item for item in pageDict['axes'] if item['name'] == dropName))


        st.write("## 3. Generate Data")

        st.write("Ready to generate:")

        st.dataframe([{'axisType':ax['axisType'],'name':ax['name'],'dataType':ax['dataType']} for ax in pageDict['axes']])

        if 'gend' not in pageDict.keys():
            pageDict['gend']=False
        if st.button("Generate data!"):
            pageDict['gend']=True
            pageDict['data']=GenerateData(pageDict['properties'],pageDict['axes'])


        if pageDict['gend']==False:
            st.write("No data generated")
            st.stop()

        df_data=pd.DataFrame(pageDict['data'])

        df_data=df_data.convert_dtypes()
        # for x in pageDict['axes']:
        #     if x['dataType']=="quantity":
        #         df_data[x['name']]=df_data[x['name']].astype(float)
        #     else:
        #         df_data[x['name']]=df_data[x['name']].astype(str)

        st.dataframe(df_data)
        stTrx.DebugOutput("columns:",df_data.columns)


        st.write("## 4. Plot Data")
        st.write("Ready to plot:",pageDict['properties']['chartType'])
        # st.write(" - for",next(item for item in pageDict['axes'] if item['axisType'] == "Y")['name'])
        # st.write(" - with",next(item for item in pageDict['axes'] if item['axisType'] == "X")['name'])

        featureDict={'X':alt.X,'Y':alt.Y,'colour':alt.Color,'shape':alt.Shape,'opacity':alt.Opacity}
        setList=[]
        tipList=[]

        for e,x in enumerate(pageDict['axes']):
            axStr=x['name']+":"+dataTypeMap[x['dataType']]
            tipList.append(axStr)
            setList.append(featureDict[x['axisType']](axStr))
        stTrx.DebugOutput("tooltips:",tipList)

        if 'plotd' not in pageDict.keys():
            pageDict['plotd']=False
        if st.button("Plot data!"):
            pageDict['plotd']=True
            # the plot!
            pageDict['chart']=GetChart(df_data,pageDict['properties']['chartType'])
            if pageDict['chart']==None:
                st.stop()

            pageDict['chart']=pageDict['chart'].encode(
                *setList,
                tooltip=tipList
            ).properties(
                width=600,
                height=400
            )

        if pageDict['plotd']==False:
            st.write("No plots made")
            st.stop()

        try:
            st.altair_chart(pageDict['chart'])
        except KeyError:
            st.write("No chart defined")
