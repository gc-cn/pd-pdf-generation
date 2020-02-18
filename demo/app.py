import dash
import dash_table
import dash_core_components as dcc
import dash_design_kit as ddk
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import math
import datetime as dt
import glob
import os

app = dash.Dash(__name__)
app.title='OTD Fornitori'

theme = {
    "accent": "#FF8827",
    "accent_negative": "#ff2c6d",
    "accent_positive": "#33ffe6",
    "background_content": "#F7F9F9",
    "background_page": "#eaeaea",
    "border": "#D1D1D1",
    "border_style": {
        "name": "underlined",
        "borderTopWidth": 0,
        "borderRightWidth": 0,
        "borderLeftWidth": 0,
        "borderBottomWidth": "1px",
        "borderBottomStyle": "solid",
        "borderRadius": 0,
        "inputFocus": {
            "outline": "transparent"
        }
    },
    "breakpoint_font": "1100px",
    "breakpoint_stack_blocks": "1100px",
    "colorway": [
        "#ff8827", #arancione
        "#66c2a5", #verde
        "#8da0cb", #blu
        "#e78ac3", #rosa
        "#a6d854",
        "#ffd92f",
        "#e5c494",
        "#b3b3b3"
    ],
    "colorscale": [
        "#ff8827",
        "#ff9542",
        "#ffa35b",
        "#ffb072",
        "#ffbd89",
        "#ffcaa0",
        "#ffd7b8",
        "#ffe4cf",
        "#fff2e7",
        "#ffffff"
    ],
    "font_family": "Open Sans",
    "font_size": "12px",
    "font_size_smaller_screen": "2px",
    "font_family_header": "Dosis",
    "font_size_header": "24px",
    "font_family_headings": "Dosis",
    "text": "#6D6D6D"
}

#dizionario che collega il nome della categoria selezionata all'interno della sezione dei confronti con il nome del campo

Legenda_Nome_Campo = {"Fornitore":'Fornitore', "Tipo Ordine":"TipoOrdine", "Descrizione Classe Articolo":"DescrizioneClasse", "Descrizione Gruppo Articolo":'DescrizioneGruppo'}

# definizione valori ed etichette dei selettori delle ascisse e delle ordinate dello scatter plot

indicators_x = ['QtaOrdinata', 'DataConsegnaPrevista','DataOrdine']
indicators_y = ['ritardoSuPrevista', 'ritardoSuConfermata']
labels_x = ['Lotto Medio Acquisto', 'Data Prevista di Consegna', "Data Riga d'Ordine"]
labels_y = ['Ritardo su Prevista', 'Ritardo su Confermata']

legende = {'QtaOrdinata': 'Lotto Medio Acquisto', 'DataOrdine': "Data Riga d'Ordine",'DataConsegnaPrevista': 'Data Prevista di Consegna','ritardoSuPrevista':'Ritardo su Prevista','ritardoSuConfermata' :'Ritardo su Confermata'}

controls1 = [
    {
        'label': 'Fornitore',
        'control': dcc.Dropdown(
            id='crossfilter-fornitore',
            value='Tutti'
        ),
    },
    {
        'label': 'Tipo Ordine',
        'control': dcc.Dropdown(
            id='crossfilter-tipo-ordine',
            value='Tutti'
        ),
    },
    {
        'label': 'Descrizione Classe Articolo',
        'control': dcc.Dropdown(
            id='crossfilter-classe',
            value='Tutti'
        ),
    },
    {
        'label': 'Descrizione Gruppo Articolo',
        'control': dcc.Dropdown(
            id='crossfilter-gruppo',
            value='Tutti'
        ),
    },
    {
        'label': 'Periodo',
        'control': dcc.RadioItems(
            id = "crossfilter-periodo",
            options=[
                {'label': i, 'value': i} 
                for i in ['Mese', 'Trimestre']
            ],
            value='Mese'
        ),
    },
]
    
controls2 = [
    {
        'label': 'Categoria di Confronto',
        'control': dcc.Dropdown(
            id='crossfilter-categoria',
            options=[
                {'label': i, 'value': i} 
                for i in ["Fornitore", "Tipo Ordine", "Descrizione Classe Articolo", "Descrizione Gruppo Articolo"]
            ],
            value = "Fornitore"
        ),
    },
    {
        'label': 'Elementi di Confronto',
        'control': dcc.Dropdown(
            id='crossfilter-valori',
            multi = True,
            value = "Tutti"
        ),
    },
    {
        'label': 'Grandezza da Confrontare',
        'control': dcc.Dropdown(
            id='grandezza',
            options=[
                {'label': i, 'value': i} 
                for i in ["% OTD", "% Conferme", "% Ritardo", "% Anticipo", "% Lieve", "% Medio", "% Grave", "Righe d'Ordine"]
            ],
            value="% OTD"
        ),
    },
]
    
controls3 = [
    {
        'label': 'x',
        'control': dcc.Dropdown(
            id='crossfilter-xaxis-column',
            options=[{'label': i, 'value': j} for i,j in zip(labels_x, indicators_x)],
            value = 'QtaOrdinata'
        ),
    },
    {
        'control': dcc.RadioItems(
            id='xaxis-type',
            options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
            value='Log',
            labelStyle={'display': 'inline-block'}
        ),
    },
    {
        'label': 'y',
        'control': dcc.Dropdown(
            id='crossfilter-yaxis-column',
            options=[{'label': i, 'value': j} for i,j in zip(labels_y, indicators_y)],
            value='ritardoSuConfermata'
        )
    },
    {
        'control': dcc.RadioItems(
            id='yaxis-type',
            options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
            value='Linear',
            labelStyle={'display': 'inline-block'}
        ),
    },
]

app.layout=ddk.App(show_editor=False, theme = theme, 
    children = [
        html.Div(
            dt.date.today().strftime('%d/%m/%Y'),
            id='data_report',
            style={'display': 'none'}, 
        ),
        html.Div(
            id='dataframe',
            style={'display': 'none'}, 
        ),
        html.Div(
            id='lid',
            style={'display': 'none'}, 
        ),
        html.Div(
            id='lunghezza',
            
        ),
        ddk.Header(
            style = {"height":"60px"},
            children = [
                ddk.Logo(src = 'http://crossnova.com/wp-content/uploads/2017/02/crossnova.png', style = {"height":"50px"}),
                ddk.Title("Title"),
                html.Button(
                    "Print",
                    id='las-print'
                ),
                html.Button(
                    "Update",
                    id='update',
                    style={'position':'relative','left':'10px'}
                )
            ]   
        ),

        html.Div(
            id="sel_fil", 
            style={'display': 'none'}, 
            children=[
                html.Span("Filtri selezionati ", style={'color':"#ff8827"}),
                html.Span('Fornitore ', style={'color':"#66c2a5"}),
                html.Span(id='fornit'),
                html.Span(' Tipo Ordine ', style={'color':"#66c2a5"}),
                html.Span(id='tipord'),
                html.Span(' Descrizione Classe Articolo ', style={'color':"#66c2a5"}),
                html.Span(id='dca'),
                html.Span(' Descrizione Gruppo Articolo ', style={'color':"#66c2a5"}),
                html.Span(id='dga'),
            ]
        ),
        
        ddk.Row([
            ddk.Block(
                width = 25,
                children = [
                    ddk.ControlCard(
                        shadow_weight='medium',
                        title = [
                            ddk.Icon(icon_name = "filter",style = {"margin-right":"10px"}),
                            "Filtri"
                        ],
                        controls = controls1,
                        style={'height':'calc(100vh - 100px)'}
                    )
                ]
            ),
            ddk.Block(
                width = 75, 
                children = [
                    ddk.Block([
                        ddk.DataCard(
                            id='otd_value',
                            style={'height':'calc(15vh - 20px)'},
                            label = "OTD",
                            icon = "calendar-check",
                            width=100,
                            #style={'height':'20vh'}
                        ),
                        ddk.DataCard(
                            id = "conferme_value",
                            style={'height':'calc(15vh - 20px)'},
                            label = "Conferma Ordine",
                            icon = "hands-helping",
                            width=100,
                        ),
                        ddk.DataCard(
                            id = "ordini_value",
                            style={'height':'calc(15vh - 20px)'},
                            label = "Righe d'Ordine",
                            color = '#ff8827',
                            icon = "bars",
                            width=100,
                            #style={'height':'20vh'}
                        )
                    ],width=40),
                    ddk.Block([
                        ddk.Card(
                            title="OTD, Anticipo e Ritardo",
                            style={'height':'calc(50vh - 35px)'},
                            width=100,
                            children=[
                                ddk.Graph(
                                    id='anticipo_ritardo',
                                    style={'height':'calc(50vh - 90px)'},
                                    config={'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'sendDataToCloud'], 'displaylogo':False}          
                                )        
                                    
                            ]
                            
                        )
                    ], width=30),
                    ddk.Block([
                        ddk.Card(
                            title="OTD, Gravità Anticipo/Ritardo",
                            style={'height':'calc(50vh - 35px)'},
                            width=100,
                            children=[
                                ddk.Graph(
                                    id='lieve_medio_grave',
                                    style={'height':'calc(50vh - 90px)'},
                                    config={'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'sendDataToCloud'], 'displaylogo':False}          
                                )        
                                    
                            ]
                            
                        )
                    ], width=30),
                    ddk.Block([
                        ddk.Card(
                            shadow_weight='medium',
                            style={'height':'calc(40vh - 35px)'},
                            children = ddk.Graph(
                                id='date_graph',
                                style = {"height":"calc(40vh - 55px)"},
                                config={'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'sendDataToCloud'], 'displaylogo':False}
                            )
                        )        
                    ])
                ]
            ),
        ]),
        
        html.Div(id='interruzione1'),
        
        html.Div(id='interruzione'),

        ddk.SectionTitle('Confronti'),
        
        html.Div(id="sel_conf", style={'display': 'none'}),

        ddk.Card(
            title = [
                ddk.Icon(icon_name = "filter",style = {"margin-right":"10px"}),
                "Data Ordine"
            ],
            padding=15,
            style = {"height":"calc(20vh)"},
            shadow_weight='medium',
            children = [
                dcc.RangeSlider(
                    id = "selezione-intervallo",
                    min = 0
                )
            ]
        ),
        
        ddk.Block([
            ddk.ControlCard(
                style = {"height":"calc(100vh - 250px)"},
                shadow_weight='medium',
                title = [
                    ddk.Icon(icon_name = "filter",style = {"margin-right":"10px"}),
                    "Filtri"
                ],
                controls = controls2
            ),        
        ],  width = 25),
         
        ddk.Block([

        ], width = 75),

        html.Div(id='interruzione2'),
        
        html.Div(id='interruzione3'),

        ddk.Card(
            shadow_weight='medium',
            children = [         
                dash_table.DataTable(
                    id = 'tabella_confronti', 
                    css=[{
                            'selector': '.dash-cell div.dash-cell-value',
                            'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                    }],
                    style_header={'fontWeight': 'bold'},
                    style_cell={
                        "font_family": "Open Sans",
                        'textAlign':'left',
                        'whiteSpace': 'no-wrap',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': 0,
                    },
                    style_cell_conditional=[
                    {'if': {'column_id': 'Elementi'},
                    'width': '25%'}
                    ],
                    columns =[{'id':i, 'name':i} for i in ["Elementi", "% OTD", "% Conferme", "% Ritardo", 
                                                        "% Anticipo", "% Lieve","% Medio", "% Grave", "Righe d'Ordine"]]
                )
            ]
        ),
    ]
)
    
#funzione che permette di filtrare i dati sulla base dei filtri impostati
                    
def filtra_data(df,tipo_ordine, classe, gruppo, fornitore):
  dff = df
  if tipo_ordine == 'Tutti':
    df1 = dff
  else:
    df1 = dff[dff["TipoOrdine"] == tipo_ordine] 
  
  if classe =='Tutti':
    df2 = df1
  else:
    df2 = df1[df1['DescrizioneClasse'] == classe]
    
  if gruppo =='Tutti':
    df3 = df2
  else:
    df3 = df2[df2['DescrizioneGruppo'] == gruppo]
    
  if fornitore == 'Tutti':
    df4 = df3
  else:
    df4 = df3[df3['Fornitore'] == fornitore]

  return df4

#funzione che permette di filtrare i dati sulla base dei filtri impostati, compreso il periodo
                    
def filtra_data_periodo(df,tipo_ordine, classe, gruppo, fornitore, periodo,Legenda_Indice_Data):
  dff = df
  if tipo_ordine == 'Tutti':
    df1 = dff
  else:
    df1 = dff[dff["TipoOrdine"] == tipo_ordine] 
  
  if classe =='Tutti':
    df2 = df1
  else:
    df2 = df1[df1['DescrizioneClasse'] == classe]
    
  if gruppo =='Tutti':
    df3 = df2
  else:
    df3 = df2[df2['DescrizioneGruppo'] == gruppo]
    
  if fornitore == 'Tutti':
    df4 = df3
  else:
    df4 = df3[df3['Fornitore'] == fornitore]
  
  df5 = df4[(df4['DataOrdine']<Legenda_Indice_Data[periodo[1]])&(df4['DataOrdine']>= Legenda_Indice_Data[periodo[0]])]

  return df5

#funzione che calcola l'OTD

def calcolo_otd (data):
    ordini = data['ritardoSuConfermata'].count()
    dfilt = data[(data["ritardoSuConfermata"]<5) & (data["ritardoSuConfermata"]>-5)]
    ordini_OT = dfilt["ritardoSuConfermata"].count()
    otd = ordini_OT/ordini*100
    arrotondato = round(otd,2)
    return arrotondato

#funzione che calcola la % di ordini in anticipo

def calcolo_anticipo (data):
    ordini = data['ritardoSuConfermata'].count()
    dfilt = data[data["ritardoSuConfermata"]<=-5]
    ordini_anticipo = dfilt["ritardoSuConfermata"].count()
    anticipo = ordini_anticipo/ordini*100
    arrotondato = round(anticipo,2)
    return arrotondato

#funzione che calcola la % di ordini in ritardo

def calcolo_ritardo (data):
    ordini = data['ritardoSuConfermata'].count()
    dfilt = data[data["ritardoSuConfermata"]>=5]
    ordini_ritardo = dfilt["ritardoSuConfermata"].count()
    ritardo = ordini_ritardo/ordini*100
    arrotondato = round(ritardo,2)
    return arrotondato

#funzione che calcola la % di ordini in ritardo/anticipo lieve

def calcolo_lieve (data):
    ordini = data['ritardoSuConfermata'].count()
    dfilt = data[(data["ritardoSuConfermata"].abs()>=5) & (data["ritardoSuConfermata"].abs()<10)]
    ordini_lieve = dfilt["ritardoSuConfermata"].count()
    lieve = ordini_lieve/ordini*100
    arrotondato = round(lieve,2)
    return arrotondato

#funzione che calcola la % di ordini in ritardo/anticipo medio

def calcolo_medio (data):
    ordini = data['ritardoSuConfermata'].count()
    dfilt = data[(data["ritardoSuConfermata"].abs()>=10) & (data["ritardoSuConfermata"].abs()<15)]
    ordini_medio = dfilt["ritardoSuConfermata"].count()
    medio = ordini_medio/ordini*100
    arrotondato = round(medio,2)
    return arrotondato

#funzione che calcola la % di ordini in ritardo/anticipo grave

def calcolo_grave (data):
    ordini = data['ritardoSuConfermata'].count()
    dfilt = data[data["ritardoSuConfermata"].abs()>=15]
    ordini_grave = dfilt["ritardoSuConfermata"].count()
    grave = ordini_grave/ordini*100
    arrotondato = round(grave,2)
    return arrotondato

#funzione che calcola la percentuale di conferme 

def calcolo_conferme (data):
    conferme = sum(data['DataConsegnaConfermataFornitore'])/data['DataConsegnaConfermataFornitore'].count()*100
    arrotondato = round(conferme,2)
    return arrotondato

#funzione che definisce la colorazione delle etichette degli indicatori sulla base del loro valore (valore alto -> buono)

def colora_se_diretto (valore):
    if valore is not None:
        valore = float(valore.split(" ") [0])
        if 33.33 <= valore <= 66.67:
            return 'var(--colorway-5)'
        elif valore < 33.33:
            return '#d62728'
        else:
            return 'var(--colorway-4)'
    else:
        return 'var(--colorway-5)'

#funzione che definisce la colorazione delle etichette degli indicatori sulla base del loro valore (valore alto -> cattivo)

def colora_se_inverso (valore):
    if valore is not None:
        valore = float(valore.split(" ") [0])
        if 33.33 <= valore <= 66.67:
            return 'var(--colorway-5)'
        elif valore < 33.33:
            return 'var(--colorway-4)'
        else:
            return "#d62728"
    else:
        return 'var(--colorway-5)'

#decoratore che aggiorna il dataframe e definisce la stringa di last update della app

@app.callback(
    dash.dependencies.Output('dataframe', 'children'),
    [dash.dependencies.Input('update', 'n_clicks')
     ])   
def update_df(n):
    list_of_files = glob.glob('{}/*.pkl'.format(os.getcwd()))
    latest_file = max(list_of_files, key=os.path.getctime)
    lunghezza=len(latest_file)
    if latest_file is not None:
        df = pd.read_pickle(latest_file)
        df['DataConsegnaPrevista'] = pd.to_datetime(df['DataConsegnaPrevista'])
        df['DataConsegnaPrevista'] = df['DataConsegnaPrevista'].dt.strftime('%Y-%m-%d')
        df['DataOrdine'] = pd.to_datetime(df['DataOrdine'])
        max_data=max(df['DataOrdine'])
        max_anno=max_data.year
        df['DataOrdine'] = df['DataOrdine'].dt.strftime('%Y-%m-%d')
        df['DataConsegnaAvvenuta'] = pd.to_datetime(df['DataConsegnaAvvenuta'])
        df['DataConsegnaAvvenuta'] = df['DataConsegnaAvvenuta'].dt.strftime('%Y-%m-%d')
        df_small=df[df['DataOrdine']>='{}-01-01'.format(max_anno)]
        dff=df_small.to_json(date_format='iso', orient='split')
        return dff
    else:
        return None, None

#decoratore che aggiorna le etichette dei dropdown dei filtri e le date del rangeslider

@app.callback(
    [dash.dependencies.Output('crossfilter-fornitore', 'options'),
     dash.dependencies.Output('crossfilter-tipo-ordine', 'options'),
     dash.dependencies.Output('crossfilter-classe', 'options'),
     dash.dependencies.Output('crossfilter-gruppo', 'options'),
     dash.dependencies.Output('selezione-intervallo', 'max'),
     dash.dependencies.Output('selezione-intervallo', 'marks'),
     dash.dependencies.Output('selezione-intervallo', 'value'),
     dash.dependencies.Output('lid', 'children')],
    [dash.dependencies.Input('dataframe', 'children')
     ])   
def update_dropdown(jdf):
    if jdf is not None:
        df = pd.read_json(jdf, orient='split')

        df['DataConsegnaPrevista'] = pd.to_datetime(df['DataConsegnaPrevista'])
        df['DataOrdine'] = pd.to_datetime(df['DataOrdine'])

        #definizione degli elementi dei menù a tendina dei filtri

        lista = df["TipoOrdine"].unique().tolist()
        indicatori_tipo_ordine = [x for x in lista if str(x)!='nan']
        indicatori_tipo_ordine = sorted (indicatori_tipo_ordine)
        indicatori_tipo_ordine = ["Tutti"] + indicatori_tipo_ordine

        lista = df['DescrizioneClasse'].unique().tolist()
        indicatori_classe = [x for x in lista if str(x)!='nan']
        indicatori_classe = sorted (indicatori_classe)
        indicatori_classe = ["Tutti"] + indicatori_classe

        lista = df['DescrizioneGruppo'].unique().tolist()
        indicatori_gruppo = [x for x in lista if str(x)!='nan']
        indicatori_gruppo = sorted (indicatori_gruppo)
        indicatori_gruppo = ["Tutti"] + indicatori_gruppo

        lista = df['Fornitore'].unique().tolist()
        indicatori_fornitore = [x for x in lista if str(x)!='nan']
        indicatori_fornitore = sorted (indicatori_fornitore)
        indicatori_fornitore = ["Tutti"] + indicatori_fornitore

        of=[
            {'label': i, 'value': i}
            for i in indicatori_fornitore
        ]

        oto=[
            {'label': i, 'value': i}
            for i in indicatori_tipo_ordine
        ]

        oc=[
            {'label': i, 'value': i}
            for i in indicatori_classe
        ]

        og=[
            {'label': i, 'value': i}
            for i in indicatori_gruppo
        ]

        ## CREAZIONE LISTA DATE RANGESLIDER

        #data ordine minima e massima
        min_data=min(df['DataOrdine'])
        max_data=max(df['DataOrdine'])

        #mese e anno data ordine minima 
        min_data_month_v=min_data.month
        min_data_year_v=min_data.year

        #mese e anno data ordine massima
        max_data_month_v=max_data.month
        max_data_year_v=max_data.year

        #creazione lista anni sulla base dell'anno data ordine minima e dell'anno data ordine massima
        lista_anni=[]
        for i in range(min_data_year_v,max_data_year_v+1):
            lista_anni.append(i)

        #lista mesi/anno data ordine minima
        mesi_min=[]
        if len(lista_anni)==1:
            for i in range(min_data_month_v,max_data_month_v+1):
                mesi_min.append(i)
            date_min=[]
            for i in mesi_min:
                if len(str(i))==1:
                    date_min.append('0{}/{}'.format(i,str(min_data_year_v)[2:]))
                else:
                    date_min.append('{}/{}'.format(i,str(min_data_year_v)[2:]))
            massimo=len(date_min)-1
            marks={date_min.index(i):i for i in date_min}
            value=[0,len(date_min)-1]
            date_val=[]
            for i in mesi_min:
                date_val.append(dt.datetime(min_data_year_v,i,1))
            indici=range(len(date_val))
            Legenda_Indice_Data=dict(zip(indici,date_val))
        else:
            while min_data_month_v<=12:
                mesi_min.append(min_data_month_v)
                min_data_month_v+=1

            date_min=[]
            for i in mesi_min:
                if len(str(i))==1:
                    date_min.append('0{}/{}'.format(i,str(min_data_year_v)[2:]))
                else:
                    date_min.append('{}/{}'.format(i,str(min_data_year_v)[2:]))

            #lista mesi/anno data ordine massima
            mesi_max=[]
            if max_data_month_v==12:
                for i in range(1,max_data_month_v+1):
                    mesi_max.append(i)
                mesi_max+=[1]
            else:    
                for i in range(1,max_data_month_v+2):
                    mesi_max.append(i)

            date_max=[]
            if max_data_month_v==12:
                for i in mesi_max:
                    if len(str(i))==1:
                        date_max.append('0{}/{}'.format(i,str(max_data_year_v)[2:]))
                    else: 
                        date_max.append('{}/{}'.format(i,str(max_data_year_v)[2:]))
                date_max.append('01/{}'.format(max_data_year_v+1))        
            else:    
                for i in mesi_max:
                    if len(str(i))==1:
                        date_max.append('0{}/{}'.format(i,str(max_data_year_v)[2:]))
                    else: 
                        date_max.append('{}/{}'.format(i,str(max_data_year_v)[2:]))

            #lista mesi/anni date ordine intermedie
            date_int=[]
            for i in lista_anni[1:len(lista_anni)-2]:
                for j in range(1,13):
                    if len(str(i))==1:
                        date_int.append('0{}/{}'.format(j,i[2:]))

            #lista contenente le opzioni di date contenute all'interno del rangeslider
            date=date_min+date_max+date_int
            
            massimo=len(date)-1
            marks={date.index(i):i for i in date}
            value=[0,len(date)-1]

            ## CREAZIONE DIZIONARIO INDICE RANGESLIDER <-> VALORE DATA

            date_val=[]

            # popolamento valori date per l'anno minimo della data ordine
            for i in mesi_min:
                date_val.append(dt.datetime(min_data_year_v,i,1))

            # popolamento valori date per gli anni intermedi della data ordine
            for i in lista_anni[1:len(lista_anni)-2]:
                for j in range(1,13):
                    date_val.append(dt.datetime(i,j,1))

            # popolamento valori date per l'anno massimo della data ordine
            if max_data_month_v==12:
                for i in mesi_max[:len(mesi_max)-2]:
                    date_val.append(dt.datetime(max_data_year_v,i,1))
                date_val.append(dt.datetime(max_data_year_v+1,1,1))
            else:
                for i in mesi_max:
                    date_val.append(dt.datetime(max_data_year_v,i,1))

            indici=range(len(date_val))
            Legenda_Indice_Data=dict(zip(indici,date_val))

        return of, oto, oc, og, massimo, marks, value, Legenda_Indice_Data
    else:
        return [],[],[],[],0,{},[], {}

#decoreatore che aggiorna il filtro selezionato sul fornitore 

@app.callback(
    dash.dependencies.Output('fornit', 'children'),
    [dash.dependencies.Input('crossfilter-fornitore', 'value')
     ])   
def update_fornit(fornitore):
    return fornitore

#decoreatore che aggiorna il filtro selezionato sul tipo ordine 

@app.callback(
    dash.dependencies.Output('tipord', 'children'),
    [dash.dependencies.Input('crossfilter-tipo-ordine', 'value')
     ])   
def update_tipord(tipord):
    return tipord

#decoreatore che aggiorna il filtro selezionato sulla classe articolo

@app.callback(
    dash.dependencies.Output('dca', 'children'),
    [dash.dependencies.Input('crossfilter-classe', 'value')
     ])   
def update_dca(dca):
    return dca

#decoreatore che aggiorna il filtro selezionato sul gruppo articolo

@app.callback(
    dash.dependencies.Output('dga', 'children'),
    [dash.dependencies.Input('crossfilter-gruppo', 'value')
     ])   
def update_dga(dga):
    return dga

@app.callback(
    [dash.dependencies.Output('otd_value', 'value'),
     dash.dependencies.Output('otd_value', 'sub'),
     dash.dependencies.Output('conferme_value', 'value'),
     dash.dependencies.Output('conferme_value', 'sub'),
     dash.dependencies.Output('ordini_value', 'value'),
     dash.dependencies.Output('anticipo_ritardo', 'figure'),
     dash.dependencies.Output('lieve_medio_grave', 'figure')],
    [dash.dependencies.Input('crossfilter-classe', 'value'),
     dash.dependencies.Input('crossfilter-tipo-ordine', 'value'),
     dash.dependencies.Input('crossfilter-gruppo', 'value'),
     dash.dependencies.Input('crossfilter-fornitore', 'value'),
     dash.dependencies.Input('dataframe', 'children')
     ])   
def update_otd(classe, tipo_ordine,gruppo,fornitore,jdf):
    if jdf is not None:
        df = pd.read_json(jdf, orient='split')

        df['DataConsegnaPrevista'] = pd.to_datetime(df['DataConsegnaPrevista'])
        df['DataOrdine'] = pd.to_datetime(df['DataOrdine'])
        
        dfilt = filtra_data(df,tipo_ordine,classe,gruppo,fornitore)

        #valore e numeratore e denominatore OTD

        ordini = dfilt['ritardoSuConfermata'].count()
        dfilt_ot = dfilt[(dfilt["ritardoSuConfermata"]<5) & (dfilt["ritardoSuConfermata"]>-5)]
        ordini_ot = dfilt_ot["ritardoSuConfermata"].count()
        otd = round((ordini_ot/ordini)*100,2)

        #valore e numeratore e denominatore della percentuale delle conferme

        confermate = sum(dfilt['DataConsegnaConfermataFornitore'])
        conferme = round((confermate/ordini)*100,2)
        
        #torta ot, anticipo, ritardo

        labels=['OTD', 'Ritardo','Anticipo']
        valori=[]

        valori.append(ordini_ot)
        
        rit = dfilt[dfilt["ritardoSuConfermata"]>=5]
        ordini_ritardo = rit["ritardoSuConfermata"].count()
        valori.append(ordini_ritardo)
        
        ant = dfilt[dfilt["ritardoSuConfermata"]<=-5]
        ordini_anticipo = ant["ritardoSuConfermata"].count()
        valori.append(ordini_anticipo)
        
        d = go.Pie(
            labels=labels,
            values=valori,
            sort=False,
            marker=dict(colors=["var(--colorway-1)","#e78ac3","#8da0cb"])
        )
    
    
        l = go.Layout(
            legend=dict(x=0.6, y=-0.1)
        )

        fig_torta_ar = go.Figure(data=[d], layout=l)

        #torta otd lieve, medio, grave

        labels=['OTD', 'Lieve','Medio', 'Grave']
        valori=[]
        
        valori.append(ordini_ot)
        
        lieve = dfilt[(dfilt["ritardoSuConfermata"].abs()>=5) & (dfilt["ritardoSuConfermata"].abs()<10)]
        ordini_lieve = lieve["ritardoSuConfermata"].count()
        valori.append(ordini_lieve)
        
        medio = dfilt[(dfilt["ritardoSuConfermata"].abs()>=10) & (dfilt["ritardoSuConfermata"].abs()<15)]
        ordini_medio = medio["ritardoSuConfermata"].count()
        valori.append(ordini_medio)
        
        grave = dfilt[dfilt["ritardoSuConfermata"].abs()>=15]
        ordini_grave = grave["ritardoSuConfermata"].count()
        valori.append(ordini_grave)
        
        d = go.Pie(
            labels=labels,
            values=valori,
            sort=False,
            marker=dict(colors=["var(--colorway-1)","#ffd92f","#ff8827", '#ff4f4f'])
        )

        fig_torta_lmg = go.Figure(data=[d], layout=l)

        return ("{:.2f} %".format(otd)), ("{} su {}".format(ordini_ot, ordini)), ("{} %".format(conferme)), ("{} su {}".format(confermate, ordini)), ordini, fig_torta_ar, fig_torta_lmg

    else:
        return None,None,None,None,None,None,None

#decoratore che aggiorna il colore dell'etichetta sulla base del valore dell'otd

@app.callback(
    dash.dependencies.Output('otd_value', 'color'),
    [dash.dependencies.Input('otd_value', 'value')])
def update_colore_OTD (valore):
    return colora_se_diretto(valore)

#decoratore che aggiorna il colore dell'etichetta sulla base del vaore della percentuale delle conferme

@app.callback(
    dash.dependencies.Output('conferme_value', 'color'),
    [dash.dependencies.Input('conferme_value', 'value')])
def update_colore_conferme (valore):
    return colora_se_diretto(valore)

#decoratore che aggiorna il grafico a barre dell'OTD sulla base dei filtri impostati
    
@app.callback(
    dash.dependencies.Output('date_graph', 'figure'),
    [dash.dependencies.Input('crossfilter-classe', 'value'),
     dash.dependencies.Input('crossfilter-tipo-ordine', 'value'),
     dash.dependencies.Input('crossfilter-gruppo', 'value'),
     dash.dependencies.Input('crossfilter-fornitore', 'value'),
     dash.dependencies.Input('crossfilter-periodo', 'value'),
     dash.dependencies.Input('dataframe', 'children')
     ])  
def update_data_graph(classe, tipo_ordine,gruppo,fornitore, periodo, jdf):
  if jdf is not None:
    df = pd.read_json(jdf, orient='split')

    df['DataConsegnaPrevista'] = pd.to_datetime(df['DataConsegnaPrevista'])
    df['DataOrdine'] = pd.to_datetime(df['DataOrdine'])

    dfilt = filtra_data(df, tipo_ordine,classe,gruppo,fornitore)
    
    #data ordine minima e massima
    min_data=min(df['DataOrdine'])
    max_data=max(df['DataOrdine'])

    #mese e anno data ordine minima 
    min_data_month_v=min_data.month
    min_data_year_v=min_data.year

    #mese e anno data ordine massima
    max_data_month_v=max_data.month
    max_data_year_v=max_data.year

    #creazione lista anni sulla base dell'anno data ordine minima e dell'anno data ordine massima
    lista_anni=[]
    for i in range(min_data_year_v,max_data_year_v+1):
        lista_anni.append(i)

    #lista mesi/anno data ordine minima
    mesi_min=[]
    if len(lista_anni)==1:
        for i in range(min_data_month_v,max_data_month_v+1):
            mesi_min.append(i)
        date_min=[]
        for i in mesi_min:
            if len(str(i))==1:
                date_min.append('0{}/{}'.format(i,str(min_data_year_v)[2:]))
            else:
                date_min.append('{}/{}'.format(i,str(min_data_year_v)[2:]))
        date=date_min
        date_val=[]
        for i in mesi_min:
            date_val.append(dt.date(min_data_year_v,i,1))
        lista_q=[]
        lista_q_v=[]
        q_min=min_data.quarter
        q_max=max_data.quarter
        Legenda_Quarter_Mese={1:1,2:4,3:7,4:10}
        for i in range(q_min,q_max+1):
            lista_q.append('Q{} {}'.format(i,str(min_data_year_v)[2:]))
            lista_q_v.append(dt.date(min_data_year_v,Legenda_Quarter_Mese[i],1))
    else:
        while min_data_month_v<=12:
            mesi_min.append(min_data_month_v)
            min_data_month_v+=1

        date_min=[]
        for i in mesi_min:
            if len(str(i))==1:
                date_min.append('0{}/{}'.format(i,str(min_data_year_v)[2:]))
            else:
                date_min.append('{}/{}'.format(i,str(min_data_year_v)[2:]))

        #lista mesi/anno data ordine massima
        mesi_max=[]
        for i in range(1,max_data_month_v+1):
            mesi_max.append(i)

        date_max=[] 
        for i in mesi_max:
            if len(str(i))==1:
                date_max.append('0{}/{}'.format(i,str(max_data_year_v)[2:]))
            else: 
                date_max.append('{}/{}'.format(i,str(max_data_year_v)[2:]))

        #lista mesi/anni date ordine intermedie
        date_int=[]
        for i in lista_anni[1:len(lista_anni)-2]:
            for j in range(1,13):
                if len(str(i))==1:
                    date_int.append('0{}/{}'.format(j,i[2:]))

        #asse x date opzione Mese
        date=date_min+date_max+date_int

        #definizione grandezze necessarie per i filtri sulle date
        date_val=[]
        
        # popolamento valori date per l'anno minimo della data ordine

        for i in mesi_min:
                date_val.append(dt.date(min_data_year_v,i,1))

        # popolamento valori date per gli anni intermedi della data ordine
        for i in lista_anni[1:len(lista_anni)-2]:
                for j in range(1,13):
                    date_val.append(dt.date(i,j,1))

        # popolamento valori date per l'anno massimo della data ordine
        for i in mesi_max:
            date_val.append(dt.date(max_data_year_v,i,1))
        
        #lista quarter
        lista_q=[]

        q_min=min_data.quarter
        while q_min<=4:
            lista_q.append('Q{} {}'.format(q_min,str(min_data_year_v)[2:]))
            q_min+=1

        for i in lista_anni[1:len(lista_anni)-2]:
            for j in range(1,5):
                lista_q.append('Q{} {}'.format(j,str(i)[2:]))

        q_max=max_data.quarter

        for i in range(1,q_max+1):
            lista_q.append('Q{} {}'.format(i,str(max_data_year_v)[2:]))

        #lista date quarter
        Legenda_Quarter_Mese={1:1,2:4,3:7,4:10}
        lista_q_v=[]
        q_min=min_data.quarter

        while q_min<=4:
            lista_q_v.append(dt.date(min_data_year_v,Legenda_Quarter_Mese[q_min],1))
            q_min+=1

        for i in lista_anni[1:len(lista_anni)-2]:
            for j in range(1,5):
                lista_q_v.append(dt.date(i,Legenda_Quarter_Mese[j],1))
        
        for i in range(1,q_max+1):
            lista_q_v.append(dt.date(max_data_year_v,Legenda_Quarter_Mese[i],1))

    if periodo == "Mese":
        
        datax = date
        datay = []
        datay_conferme = []
        testo = []
        testo_conferme = []
        
        if dfilt.size >0:
            dates_values=[dt.datetime.date(i) for i in dfilt['DataOrdine']]
            ref_start=date_val
            ref_end = ref_start[1:]
            if max_data_month_v==12:
                ref_end.append(dt.date(max_data_year_v+1,1,1))
            else:
                ref_end.append(dt.date(max_data_year_v,max_data_month_v+1,1))
            for i,j in zip(ref_start,ref_end):
                selection = [k>=i and k<j for k in dates_values]
                dfilt_sel = dfilt[selection]
                quanti = dfilt_sel['otdConfermata'].count()
                if(quanti>5):
                    otd = calcolo_otd(dfilt_sel)
                    conferme=calcolo_conferme(dfilt_sel)
                else:
                    otd = math.nan
                    conferme = math.nan
                    #otd = 0
                datay.append(otd)
                datay_conferme.append(conferme)
                testo.append('OTD calcolato su ' + str(quanti) +' ordini')
                testo_conferme.append('% Conferma Ordine calcolata su ' + str(quanti) +' ordini')
    else:
        
        datax = lista_q
        datay = []
        datay_conferme = []
        testo = []
        testo_conferme = []
        
        if dfilt.size >0:
            dates_values=[dt.datetime.date(i) for i in dfilt['DataOrdine']]
            ref_start = lista_q_v
            ref_end = ref_start[1:]
            if q_max==4:
                ref_end.append(dt.date(max_data_year_v+1,1,1))
            else:
                ref_end.append(dt.date(max_data_year_v,Legenda_Quarter_Mese[q_max+1],1))
            for i,j in zip(ref_start,ref_end):
                selection = [k>=i and k<j for k in dates_values]
                dfilt_sel = dfilt[selection]
                quanti = dfilt_sel['otdConfermata'].count()
                if(quanti>5):
                    otd = calcolo_otd(dfilt_sel)
                    conferme = calcolo_conferme(dfilt_sel)
                else:
                    otd = math.nan
                    conferme = math.nan
                    #otd = 0
                datay.append(otd)
                datay_conferme.append(conferme)
                testo.append('OTD calcolato su ' + str(quanti) +' ordini')
                testo_conferme.append('% Conferma Ordine calcolata su ' + str(quanti) +' ordini')              
    d1 = go.Bar(
        x=datax,
        y=datay,
        text=testo,
        name='%OTD',
        marker=dict(color="#66c2a5")
    )
    
    d2 = go.Bar(
        x=datax,
        y=datay_conferme,
        text=testo_conferme,
        name='% Conferma Ordine',
        marker=dict(color="#7676f7")
    )
    
    d=[d1,d2]
    
    l = go.Layout(
        #title='Andamento OTD su base mensile',
        xaxis = {'title': 'Data Ordine'},
        margin=go.layout.Margin(
            l=50,
            r=50
        ),
        legend=dict(x=0.4,y=-0.3)
    )

    fig = go.Figure(data=d, layout=l)
    return fig
  else:
    return None

# callback che aggiorna il testo in cui si specifica la data dell'ordine, la categoria e gli elementi di confronto

@app.callback(
    dash.dependencies.Output('sel_conf', 'children'),
    [dash.dependencies.Input('selezione-intervallo', 'value'),
     dash.dependencies.Input('crossfilter-categoria', 'value'),
     dash.dependencies.Input('crossfilter-valori', 'value'),
     dash.dependencies.Input('lid', 'children'),
     ])
def update_sel_conf(interval, cat,el,lid):
    indici=[]
    date=[]
    for i in lid:
        indici.append(int(i))
        date.append(dt.datetime.strptime(lid[i],'%Y-%m-%d'))
    Legenda_Indice_Data=dict(zip(indici,date))
    if interval is None:
        return ''
    else:
        if type(el) is list:
            return "Confronto tra {} della categoria {} nel periodo {} - {}".format(', '.join(el), cat, Legenda_Indice_Data[interval[0]], Legenda_Indice_Data[interval[1]])
        else:
            if el == 'Tutti':
                return "Confronto tra {} della categoria {} nel periodo {} - {}".format(el, cat, Legenda_Indice_Data[interval[0]], Legenda_Indice_Data[interval[1]])
            else:
                return "{} della categoria {} nel periodo {} - {}".format(el, cat, Legenda_Indice_Data[interval[0]], Legenda_Indice_Data[interval[1]])


# callback che aggiorna le opzioni del selettore dei valori per i confronti 

@app.callback(
    dash.dependencies.Output('crossfilter-valori', 'options'),
    [dash.dependencies.Input('crossfilter-classe', 'value'),
     dash.dependencies.Input('crossfilter-tipo-ordine', 'value'),
     dash.dependencies.Input('crossfilter-gruppo', 'value'),
     dash.dependencies.Input('crossfilter-fornitore', 'value'),
     dash.dependencies.Input('selezione-intervallo', 'value'),
     dash.dependencies.Input('crossfilter-categoria', 'value'),
     dash.dependencies.Input('dataframe', 'children'),
     dash.dependencies.Input('lid', 'children'),
     ])
def update_selettore(classe, tipo_ordine,gruppo,fornitore, periodo, categoria,jdf,lid):
    indici=[]
    date=[]
    for i in lid:
        indici.append(int(i))
        date.append(dt.datetime.strptime(lid[i],'%Y-%m-%d'))
    Legenda_Indice_Data=dict(zip(indici,date))
    if jdf is not None:
        df = pd.read_json(jdf, orient='split')

        df['DataConsegnaPrevista'] = pd.to_datetime(df['DataConsegnaPrevista'])
        df['DataOrdine'] = pd.to_datetime(df['DataOrdine'])
        
        dfilt = filtra_data_periodo(df,tipo_ordine,classe,gruppo,fornitore, periodo,Legenda_Indice_Data)

        if not dfilt.empty:
            ordinati = sorted(dfilt[Legenda_Nome_Campo[categoria]].unique().tolist())
            ordinati = ["Tutti"] + ordinati
            opzioni = [{'label': i, 'value':i} for i in ordinati]
            return opzioni
            return {}
    else:
        return {}

@app.callback(
    dash.dependencies.Output('tabella_confronti', 'data'),
    [dash.dependencies.Input('crossfilter-classe', 'value'),
     dash.dependencies.Input('crossfilter-tipo-ordine', 'value'),
     dash.dependencies.Input('crossfilter-gruppo', 'value'),
     dash.dependencies.Input('crossfilter-fornitore', 'value'),
     dash.dependencies.Input('selezione-intervallo', 'value'),
     dash.dependencies.Input('crossfilter-categoria', 'value'),
     dash.dependencies.Input('crossfilter-valori', 'value'),
     dash.dependencies.Input('dataframe', 'children'),
     dash.dependencies.Input('lid', 'children'),
     ])
def update_box_down(classe, tipo_ordine,gruppo,fornitore, periodo, categoria, valori,jdf,lid):
    indici=[]
    date=[]
    for i in lid:
        indici.append(int(i))
        date.append(dt.datetime.strptime(lid[i],'%Y-%m-%d'))
    Legenda_Indice_Data=dict(zip(indici,date))
    if jdf is not None or periodo is not None:
        df = pd.read_json(jdf, orient='split')

        df['DataConsegnaPrevista'] = pd.to_datetime(df['DataConsegnaPrevista'])
        df['DataOrdine'] = pd.to_datetime(df['DataOrdine'])

        dfilt = filtra_data_periodo(df,tipo_ordine,classe,gruppo,fornitore, periodo,Legenda_Indice_Data)

        if not dfilt.empty:
            # box plot del ritardo 

            if "Tutti" in valori:
                datax = dfilt[Legenda_Nome_Campo[categoria]].unique().tolist()
            else: 
                datax = [i for i in valori]       
                
            lista_ordini = []
            datay = []
                    
            if dfilt.size >0:
                for i in datax:
                    dfilt_sel = dfilt[dfilt[Legenda_Nome_Campo[categoria]]==i]
                    ordini = dfilt_sel['ritardoSuConfermata'].count()
                    lista_ordini.append(ordini)

                    ritardo = dfilt_sel['ritardoSuConfermata'].tolist()
                    datay.append(ritardo)

            #tabella dei confronti

            elem=[]
            otd_elementi = []
            conferme_elementi = []
            ritardo_elementi = []
            anticipo_elementi = []
            rit_lieve_elementi = []
            rit_medio_elementi = []
            rit_grave_elementi = []
            num_ord_elementi = []
            
            if "Tutti" in valori:
                if dfilt.size >0:
                    el = dfilt[Legenda_Nome_Campo[categoria]].unique().tolist()
                    for i in el:
                        dfilt_sel = dfilt[dfilt[Legenda_Nome_Campo[categoria]]==i]

                        if dfilt_sel['DataOrdine'].count()<6:
                            continue
                        else:
                            elem.append(i)
                            otd = calcolo_otd(dfilt_sel)
                            otd_elementi.append(otd)
                            conferme = calcolo_conferme(dfilt_sel)
                            conferme_elementi.append(conferme)
                            ritardo = calcolo_ritardo(dfilt_sel)
                            anticipo = calcolo_anticipo(dfilt_sel)
                            lieve = calcolo_lieve(dfilt_sel)
                            medio = calcolo_medio(dfilt_sel)
                            grave = calcolo_grave(dfilt_sel)
                            ritardo_elementi.append(ritardo)
                            anticipo_elementi.append(anticipo)
                            rit_lieve_elementi.append(lieve)
                            rit_medio_elementi.append(medio)
                            rit_grave_elementi.append(grave)
                            num_ord_elementi.append(dfilt_sel['DataOrdine'].count())
                            
                d = {"Elementi":elem, "% OTD":otd_elementi, "% Conferme":conferme_elementi, "% Ritardo":ritardo_elementi, 
                    "% Anticipo":anticipo_elementi , "% Lieve": rit_lieve_elementi, "% Medio": rit_medio_elementi,
                    "% Grave":rit_grave_elementi, "Righe d'Ordine":num_ord_elementi}
            else:
                if dfilt.size >0:
                    for i in valori:
                        dfilt_sel = dfilt[dfilt[Legenda_Nome_Campo[categoria]]==i]
                        
                        quanti_otd_conf = dfilt_sel['otdConfermata'].count()
                        if(quanti_otd_conf>5):
                            otd = calcolo_otd(dfilt_sel)
                        else:
                            otd = math.nan
                        otd_elementi.append(otd)
                        
                        quanti_data_conf = dfilt_sel['DataConsegnaConfermataFornitore'].count()
                        if(quanti_data_conf>5):
                            conferme = calcolo_conferme(dfilt_sel)
                        else:
                            conferme = math.nan
                        conferme_elementi.append(conferme)
                
                        quanti_rit_conf = dfilt_sel['ritardoSuConfermata'].count()
                        if(quanti_rit_conf>5):
                            ritardo = calcolo_ritardo(dfilt_sel)
                            anticipo = calcolo_anticipo(dfilt_sel)
                            lieve = calcolo_lieve(dfilt_sel)
                            medio = calcolo_medio(dfilt_sel)
                            grave = calcolo_grave(dfilt_sel)
                        else:
                            ritardo = math.nan
                            anticipo = math.nan
                            lieve = math.nan
                            medio = math.nan
                            grave = math.nan
                        ritardo_elementi.append(ritardo)
                        anticipo_elementi.append(anticipo)
                        rit_lieve_elementi.append(lieve)
                        rit_medio_elementi.append(medio)
                        rit_grave_elementi.append(grave)
                        
                        num_ord_elementi.append(quanti_rit_conf)
                            
                d = {"Elementi":valori, "% OTD":otd_elementi, "% Conferme":conferme_elementi, "% Ritardo":ritardo_elementi, 
                    "% Anticipo":anticipo_elementi , "% Lieve": rit_lieve_elementi, "% Medio": rit_medio_elementi,
                    "% Grave":rit_grave_elementi, "Righe d'Ordine":num_ord_elementi}
            
            matrice = pd.DataFrame(data=d)
            matrice = matrice.sort_values(by=["Righe d'Ordine"], ascending = False)
            data = matrice.to_dict('rows') 

            return data

        else:
            return []
    else:
        return []

server = app.server
if __name__ == '__main__':
    app.run_server(port = 4004, host = '0.0.0.0')