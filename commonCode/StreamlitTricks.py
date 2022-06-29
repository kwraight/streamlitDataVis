### standard
import streamlit as st
### custom
import os
import pandas as pd
import ast
import csv
import json
from datetime import datetime
import altair as alt
### PDB stuff
import core.stInfrastructure as infra


#####################
### useful functions
#####################

def Tryeval(val):
    # https://stackoverflow.com/questions/2859674/how-to-convert-list-of-strings-to-their-correct-python-types
    try:
        val = ast.literal_eval(val)
    except ValueError:
        pass
    except SyntaxError:
        pass
    return val

def MatchType(oldObj,newObj):
    matchMap={'int':int,'float':float,'list':list,'dict':dict,'str':str}
    # st.write(f"old:{oldObj}, new:{newObj}")
    # st.write("old type:",type(oldObj).__name__)
    try:
        return matchMap[ type(oldObj).__name__ ](newObj)
    except KeyError:
        st.write(f"automatic mapping failed for value: {newObj} (let it be)")
        # st.write(f"old: {oldObj}, new: {newObj}")
        # st.write(f"old type: {type(oldObj).__name__}, new type: {type(newObj).__name__}")
        return newObj

def DebugOutput(inStr,inObj=None,dbgLvl=None):
    if st.session_state.debug:
        outStr="**DEBUG** "+inStr
        if dbgLvl!=None:
            try:
                outStr=outStr.replace('DEBUG','DEBUG('+str(dbgLvl)+')')
                if st.session_state.debugLevel<=dbgLvl:
                    st.write(outStr)
                    if inObj!=None:
                        st.write(inObj)
            except AttributeError:
                st.write(outStr)
                if inObj!=None:
                    st.write(inObj)
        else:
            st.write(outStr)
            try:
                if inObj!=None:
                    st.write(inObj)
            except ValueError:
                st.write(inObj)


def ColourCells(s, df, colName, flip=False):
    thisRow = pd.Series(data=False, index=s.index)
    colours=['red','blue','green','orange','purple''yellow','pink','lightblue','lightgreen']*3
    names=list(df[colName].unique())
    if flip:
        return ['background-color: %s ; color: %s'% ('white',colours[names.index(s[colName])])]*len(df.columns)
    else:
        return ['background-color: %s ; color: %s'% (colours[names.index(s[colName])],'black')]*len(df.columns)

def Stringify(df_in,skips=[]):
    for c in df_in.columns:
        if c in skips:
            continue
        try:
            df_in[c]=df_in[c].astype(str)
        except TypeError:
            pass



def VisOrientation(df_in, textCut=0.1):
    ### based on xCol=x yCol=y textCol=text
    if df_in.empty:
        return
    ### base plot
    base = alt.Chart(df_in).encode(
        alt.X('x:N', scale=alt.Scale(paddingInner=0)),
        alt.Y('y:N', scale=alt.Scale(paddingInner=0)),
    )
    # Configure heatmap
    heatmap = base.mark_rect(stroke='black', strokeWidth=2).encode(
        color=alt.Color('x:N',
            scale=alt.Scale(scheme='viridis'),
            legend=None #alt.Legend(direction='horizontal')
        )
    )
    # Configure text
    textT = base.mark_text(baseline='bottom',size=20, dy=0).transform_calculate(label = "'text: ' + datum").encode(
        text=alt.Text('text:N'), #alt.value(['alt.datum.ave:Q', 'Line 2']),
        color=alt.condition(
            alt.datum.ave > textCut,
            alt.value('black'),
            alt.value('white')
        )
    )
    # layer plot
    df_layer=alt.layer(heatmap, textT).resolve_scale(
        y = 'independent'
    ).properties(width=df_in['x'].max()*500, height=df_in['y'].max()*500)
    # plot chart
    st.altair_chart(df_layer)
