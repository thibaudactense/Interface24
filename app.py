
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


#Chargement des données
@st.cache_data
def load_data():
    # Lecture de la base retraitée
    df = pd.read_parquet('./data.parquet')
    df = df.astype({'date_remb' : 'datetime64[ns]', 'date_soin' : 'datetime64[ns]', 'cod_prest' : str})
    return df

#Définition des fonctions moyennes

#Moyenne simple
def mean(selected_data,col1):
        sum1= selected_data[col1].sum()
        sum2= selected_data['nb_act'].sum()
        mean = sum1/sum2
        return mean

#Moyenne pondérée par la quantité
def mean_pond(selected_data,col1):
    prod = selected_data[col1]*selected_data['nb_act']
    sum1 = prod.sum()
    sum2 = selected_data['nb_act'].sum()
    mean = sum1/sum2
    return mean

#Moyenne en pourcentage
def mean_dep_pctg(df):
    div = df['mtn_dep']/df['BR']
    sum1 = div.sum()
    sum2 = df['nb_act'].sum()
    mean = sum1/sum2
    return mean*100

#Création des graphiques

def graphe_MG(df_MG,actes_dropdown,spécialité_dropdown2):

    #On sélectionne les consultattions
    
    selected_data = df_MG

    # Calcul des moyennes des différentes variables
    moyenne_mtn_dep = mean(selected_data,'mtn_dep')
    moyenne_mtn_remb = mean(selected_data,'mtn_remb')
    moyenne_BR = mean(selected_data,'BR')
    moyenne_TM = moyenne_BR - moyenne_mtn_remb
    somme_MG = moyenne_mtn_remb + moyenne_TM + moyenne_mtn_dep

    categories = [spécialité_dropdown2]
    bar_width = 0.4

    data = [
        go.Bar(
            name='Montant remboursé', 
            x=categories, y=[moyenne_mtn_remb], 
            width=bar_width, 
            hovertemplate="%{y:.0f} €",
            text=[f'<b>{moyenne_mtn_remb:.0f} €</b>'],
            textfont ={'size':20},
            textposition= 'outside',
            marker=dict(color='#C80000')
        ),
        go.Bar(
            name='Ticket modérateur', 
            x=categories, 
            y=[moyenne_TM], 
            width=bar_width, 
            hovertemplate="%{y:.0f} €",
            text=[f'<b>{moyenne_TM:.0f} €</b>'],
            textfont ={'size':20},
            textposition= 'inside',
            marker=dict(color="#FF8383")
        ),
        go.Bar(
            name="Dépassement d'honoraires", 
            x=categories, 
            y=[moyenne_mtn_dep], 
            width=bar_width, 
            hovertemplate="%{y:.2f} €",
            text=[f'<b>{moyenne_mtn_dep:.2f} €</b>'],
            textfont ={'size':20},
            textposition= 'auto',
            marker=dict(color='#B9B9B9')
        )
    ]

    layout = go.Layout(
        barmode='stack',
        height=600,
        yaxis=dict(
            title='Montant (€)',  
            range=[0, somme_MG + 5] ,
            title_font=dict(
                size=20,
                color='black'
            ),
            tickfont=dict(
                size=20,
                color='black'         
            )
        ),
        xaxis=dict(
            tickfont=dict(
                size=20,
                color='black'
            )
        ),
        legend=dict(
            x=0.5,  
            y=-0.19,  
            xanchor='center',  # Ancrage horizontal de la légende (center pour centrer)
            yanchor='bottom',  # Ancrage vertical de la légende (bottom pour aligner en bas)
            orientation='h',  # Orientation de la légende (h pour afficher en ligne)
            bgcolor='rgba(255, 255, 255, 0.5)',  # Couleur de fond de la légende (transparence)
            bordercolor='rgba(0, 0, 0, 0.5)',  # Couleur de bordure de la légende (transparence)
            font=dict(size=16)
        ),
        title=dict(
            text='Dépense moyennes  : <br> ' + actes_dropdown,
            x=0.55,  # Position x du titre (0.5 pour centrer horizontalement)
            y=0.9,  # Position y du titre (0.95 pour aligner en haut)
            xanchor='center',  # Ancrage horizontal du titre (center pour centrer)
            yanchor='top',  # Ancrage vertical du titre (top pour aligner en haut)
            font = dict(size=25)
        ),
        annotations=[
             dict(
                x=categories[0],
                y=somme_MG,
                text=f'<b>TOTAL ~ {int(somme_MG)} €</b>',
                font=dict(size=20, color='black'),
                showarrow=False,
                xshift=220,
                yshift=-180,
                bordercolor='black',
                borderwidth=3,
                borderpad=10
             )
        ],
    
    )

    fig2 = go.Figure(data=data, layout=layout)

    return fig2

def graphe_dep(df_spé):
     
     #calculs des moyennes de dépassements :
    list_spé = df_spé['prof2'].unique()

    list_mean =[]

    for prof in list_spé :
        df_spé2=df_spé[df_spé['prof2']==prof]
        moy_dep = mean(df_spé2,'mtn_dep')
        list_mean.append(moy_dep)

    #Intégration à une dataframe et tri décroissant :
    df2 = pd.DataFrame()
    df2['prof2'] = pd.DataFrame(list_spé)
    df2['mean_dep'] = pd.DataFrame(list_mean)
    df2 = df2.sort_values(by = 'mean_dep')

    #Création du graphique

    fig = go.Figure(
        data=go.Bar(x=df2['mean_dep'],
            y=df2['prof2'], 
            orientation='h',
            marker=dict(color='#C80000')
        )
    )
    
    #Réglages visuels
    fig.update_layout(
        title={
            'text': 'Dépassement moyen par spécialité',
            'x': 0.5,  # Centrer le titre horizontalement
            'xanchor': 'center',
            'yanchor': 'top',
            'font' :{'size' : 25}
        },
        xaxis_title="Montant moyen du dépassement (€)", 
        xaxis_title_font={'size':20},
        yaxis_title='Spécialités',
        yaxis_title_font={'size':20},
        height = 1000, 
        width = 1000
    )

    fig.update_traces(
        hovertemplate="<b>%{x:.1f}€</b>",
        name='',
        text=df2['mean_dep'].apply(lambda x: f"{x:.1f}€" if x < 2 else ''), 
        textposition='outside'
    )
    
    return fig

def main():
    
    ######Partie fixe######

    #Création de la page 
    st.set_page_config(page_title="Analyse dépasement honoraires",
                    page_icon=":bar_chart:",
                    layout="wide")

    #Titre de la page
    st.title("Analyse dépenses de l'Assurance Maladie en soins de ville")

    #Marge verticale gauche droite
    st.markdown(
        """
        <style>
        .stApp {
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
            padding-left: 10px;
            padding-right: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    #######################


    #Chargement données (déjà en cache)
    df = load_data()

    #on selectionne seulement les médecins spécialistes
    df_spé = df[df['cat_prof'] == "Médecins Spécialistes"]
    

    #Marge horizontal#
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    ##################

    #Graphique Omnipraticiens

    list_act_spé = ['1090','1092','1094','1098','1099','1104','1105',
                     '1107','1111','1112','1113','1114','1117','1118',
                     '1122','1140','1168','1172','1174','1191','1312',
                     '1318','1321','1322','1323','1324','1331','1351',
                     '1352','1361','1400','1401','1402','1403','1404',
                     '1405','1407','1408','1409','1410','1412','1413',
                     '1415','1416','1417','1418','1419','1420','1434',
                     '1435','1436','1451','1453','1462','1465','1470',
                     '1471','1473','1474','1475','1476','1477','2411',
                     '2412','2413','2414','2418','2426','2428']
    
    df_spé2=df[df['cod_prest'].isin(list_act_spé)]
   
    
    actes_dropdown = st.selectbox("Choisissez l'acte à détailler :", df_spé2['presta'].unique())

    df_spé3 = df_spé2[df_spé2['presta'] == actes_dropdown]
    
    
    spécialité_dropdown2 = st.selectbox('Choisissez la spécialité du médecin :', df_spé3['prof2'].unique())
    df_spé4 = df_spé3[df_spé3['prof2']==spécialité_dropdown2]

    graph2 = graphe_MG(df_spé4,actes_dropdown,spécialité_dropdown2)
    st.plotly_chart(graph2)


    #Marge horizontal#
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    ##################


    #Graphique dépassement honoraires spécialistes
    graph3 = graphe_dep(df_spé)
    st.plotly_chart(graph3)
    

    #Marge horizontal#
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    ##################

#http://172.31.99.36:8501/
    

    

if __name__ == "__main__":
    main()
