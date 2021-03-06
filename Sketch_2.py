import streamlit as st
import pandas as pd

def selector(start, df_rel, cond, dfr, dfo_ind):

    global selection, gl_config_error

    df_cur = dfr[dfr['From'] == start]
    df_cur = df_cur[df_cur['Relation type'].isin(df_rel)]
    df_cur = df_cur[df_cur['Condition'].isin(cond)]

    if len(df_cur) != 0:

        for r in df_cur.iterrows():
            if r[1]['XOR ID'] == '-':
                dfo_ind.loc[start, 'highlight_type'] = 'intermediate'
    
                selector(r[1]['To'], df_rel, cond, dfr, dfo_ind)

            else:
                df_xor = df_cur[df_cur['XOR ID'] == r[1]['XOR ID']]
                default = 'True'
                choice = []
                choice_cond = ''


                for n in df_xor.iterrows():
                  if n[1]['Condition'] == '-' and default == 'True':
                    choice = n[1]['To']

                  elif n[1]['Condition'] in cond and default == 'False':
                    gl_config_error = '>>> ERROR:','ambiguous selection. {}-{} with {}-{} for parent object {}'.format(n[1]['To'], n[1]['Condition'], choice, choice_cond,start)
                    return

                  elif n[1]['Condition'] in cond and default == 'True':
                    default = 'False'
                    choice = n[1]['To']
                    choice_cond = n[1]['Condition']

                  else:
                    choice = False

                if choice:
                    dfo_ind.loc[start, 'highlight_type'] = 'intermediate'
                    selector(choice, df_rel, cond, dfr, dfo_ind)

                else:
                  selection.append(start)

    else:
        selection.append(start)
        
depth = 0
def recur_4x (d, oid, dfr):     
    """
    recursive function to set the x-values for all Objects
    """
    global depth

    if (d < depth):
        depth = d
        
    tdf = dfr[dfr['From'] == oid]
    
    if (len(tdf) > 0):
        for j, r in tdf.iterrows():
            m = recur_4x(d-1, tdf['To'][j], dfr)
            
            if (m < depth):
                depth = m
    return depth


header = st.container()
descriptive = st.container()
uploads = st.container()
dropdowns = st.container()
error = st.container()
output = st.container()


# dataset = st.beta_container()




with header:
    st.title('Sketch 2')
    
with descriptive:
    st.markdown(
        """
        ---
        #### Gist:
         - Show that, given a product structure, \
             valid configurations can be generated \
                 using the relations between the objects \
                     and a rule set (including Exclusive Or relations)
         - Indicate ambiguous conditions \n
         
         #### Functionality:
         1. Begin at the **START** node/object, as indicated by \
             the user (dropdown of all objects in the *OBJECTS.csv*)
         2. If applicable, follow the objects that
            - are related to the **START** object by the **SELECTED** \
                relations (dropdown of all relations found in the *RELATIONS.csv* file) AND
            - have a default relation with the **START** object \
                (= no conditions), or that have the **CONDITIONS** \
                    as selected (dropdown of all conditions in the *RELATIONS.csv* file)
         3. Identify conflicts when two or more conditions are \
             selected allocated to the same XOR port of an object. \
                 See image: conditions C2 and C3 cannot be selected \
                     simultaneously. Give error message when this \
                         occurs and explain what the error situation is.
         4. Implement rule: the default relation is overruled when \
             a condition is selected for the same object on the same \
                 XOR port. (in the image: when condition C2 is selected, \
                     the "Combustion Engine B" will be the selected item,\
                         instead of "Combustion Engine A" which is the default. )
         5. Repeat this process (1 - 4) for all selected objects related to the **START** object. \n
         ---
         
        """
    )
    
with uploads:

    l_col, r_col = st.columns(2)
        
    objects_u = l_col.file_uploader('Upload Objects', 
                                    accept_multiple_files = False, 
                                    type = 'CSV')
    if objects_u is not None:
        df_obj = pd.read_csv(objects_u)
        df_obj = df_obj.fillna("-")

    relations_u = r_col.file_uploader('Upload Relations', 
                                        accept_multiple_files = False, 
                                        type = 'CSV')
    if relations_u is not None:
        df_rel = pd.read_csv(relations_u)
        df_rel = df_rel.fillna("-")
        
with dropdowns:
    results = []
    l_col, m_col, r_col = st.columns(3)

    if objects_u is not None:
        if 'Object ID' not in df_obj.columns:
            l_col.write('No object ID column found')
        else:
            start_obj = l_col.selectbox('Start object', 
                        options = df_obj['Object ID'])
    else:
        start_obj = l_col.selectbox('Start object', 
                        options = ['No objects found'])
        
    if relations_u is not None:
        conditions = m_col.multiselect('Conditions', 
                                    options = list(filter(lambda a: a != '-', df_rel['Condition'].unique())))
    else:
        conditions = m_col.multiselect('Conditions', 
                                    options = ['No conditions found'],
                                    default = ['No conditions found'])
        
    if relations_u is not None:
        rel_types = r_col.multiselect('Relation types', 
                                    options = df_rel['Relation type'].unique(),
                                    default = df_rel['Relation type'].unique()[0])
    else:
        rel_types = r_col.multiselect('Relation types', 
                                    options = ['No relations found'], 
                                    default = ['No relations found'])
        


        
with output:
    
    if objects_u is not None and relations_u is not None:
        if conditions is None:
            cds = ['-']
        else:
            cds = conditions.append('-')
            
            selection = []
            gl_config_error = ''
            selector(start_obj, rel_types, conditions, df_rel, df_obj)
            results = selection
            
            if gl_config_error != '':
                st.write(gl_config_error)
            
                st.subheader('Output table')
                st.table()
            else:
                st.subheader('Output table')
                df_results = pd.DataFrame(set(selection), columns=['Selected items'])
                df_results.index += 1
                st.table(df_results)








