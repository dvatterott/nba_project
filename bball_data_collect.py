import time
import pandas as pd
import requests
import numpy as np

def create_player_df():
    url = 'http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=0&LeagueID=00&Season=2015-16'
    response = requests.get(url)
    headers = response.json()['resultSets'][0]
    players = response.json()['resultSets'][0]['rowSet']
    players_df = pd.DataFrame(players, columns=headers['headers'])
    return players_df

def careerPer36(playerID):
    url = 'http://stats.nba.com/stats/playercareerstats?LeagueID=00&PerMode=Per36&PlayerID='+str(playerID)
    header_data = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'\
            ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 '\
            'Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9'\
            ',image/webp,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive'
        }
    try:
        response = requests.get(url,headers = header_data)
        print playerID #testing purposes
    except:
        time.sleep(5) #sometime the nba api gets mad about all the requests, so i take a quick break
        response = requests.get(url,headers = header_data)
    headers = response.json()['resultSets'][1]
    players = response.json()['resultSets'][1]['rowSet']
    players_df = pd.DataFrame(players, columns=headers['headers'])
    return players_df

def gather_bballData():
    
    import urllib2
    from bs4 import BeautifulSoup
    import pandas as pd
    import numpy as np
    import time
    
    def convert_float(val):
        try:
            return float(val)
        except ValueError:
            return np.nan
    
    az = map(chr, range(97, 123)); #list of letters in alphabet.
    del az[23] #remove x because no players with a last name starting with X!
    #az = 'c'
    basic_url = 'http://www.basketball-reference.com'
    players1 = 0
    
    #loop through letters in alphabet
    for letters in az: #loop through last names
        print letters #let me know where we're at
        url = basic_url+'/players/'+letters+'/' 
        time.sleep(1) #don't overload bball ref
        try:
            html = urllib2.urlopen(url)
        except:
            time.sleep(5) #don't overload bball ref
            html = urllib2.urlopen(url, timeout=5)
        soup = BeautifulSoup(html,"lxml")
        
        #get list of players 
        num_players = len(soup.select('tbody')[0].findAll('tr')) #number of players on page. 
        #num_players = 4;
        
        #loop through player list
        for players in np.arange(num_players):
            if int(soup.select('tbody')[0].findAll('tr')[players].findAll('td')[2].text) > 1979: #only get data from players after 3 point line
                players1+=1
                
                #print soup.select('tbody')[0].findAll('tr')[players].findAll('td')[0].findAll('a', href=True)[0]['href']
                #used this for debugging
                
                #get data off web
                url2 = basic_url+soup.select('tbody')[0].findAll('tr')[players].findAll('td')[0].findAll('a', href=True)[0]['href']
                time.sleep(1) #slow things down so bball ref doesn't get mad
                try:
                    html2 = urllib2.urlopen(url2)
                except:
                    time.sleep(5) #don't overload bball ref
                    html2 = urllib2.urlopen(url2, timeout=5)
                soup2 = BeautifulSoup(html2,"lxml")
                
                #collect data from html
                name = [soup2.findAll('h1')[0].text]
                year = [convert_float(soup2.findAll('tbody')[2].findAll('tr')[0].select('td')[0].text[0:4])]
                per36 = [convert_float(x.text) for x in soup2.findAll('tfoot')[2].findAll('tr')[0].select('td')[5:]]
                RTG = [convert_float(x.text) for x in soup2.findAll('tfoot')[3].findAll('tr')[0].select('td')[-2:]]
                adv = [convert_float(x.text) for i,x in enumerate(soup2.findAll('tfoot')[4].findAll('tr')[0].select('td')[7:]) if i != 12 and i != 17]
                out = name+year+per36+RTG+adv
                
                #make dataframe
                if players1==1: #first player
                    df = pd.DataFrame(out).T
                else:
                    df = df.append(pd.Series(out),ignore_index=True)
    
    #create column headers
    name = ['Name']
    year = ['Year']
    headers1 = [x.text for x in soup2.findAll('thead')[2].findAll('tr')[0].select('th')[5:]]
    headers2 = [x.text for x in soup2.findAll('thead')[3].findAll('tr')[0].select('th')[-2:]]
    headers3 = [x.text for x in soup2.findAll('thead')[4].findAll('tr')[0].select('th')[7:] if len(x.text)>0]
    headers = name+year+headers1+headers2+headers3
    df.columns = headers
    df.index = range(np.size(df,0))
    df = df.fillna(0)
    
    return df

def gather_rookie_bballData():
    
    import urllib2
    from bs4 import BeautifulSoup
    import pandas as pd
    import numpy as np
    import time
    import os
    os.environ['http_proxy']=''
    
    def convert_float(val):
        try:
            return float(val)
        except ValueError:
            return np.nan
    
    az = map(chr, range(97, 123)); #list of letters in alphabet.
    del az[23] #remove x because no players with a last name starting with X!
    basic_url = 'http://www.basketball-reference.com'
    players1 = 0
    
    #loop through letters in alphabet
    for letters in az: #loop through last names
        print letters #let me know where we're at
        url = basic_url+'/players/'+letters+'/' 
        
        try:
            html = urllib2.urlopen(url)
        except:
            time.sleep(5) #don't overload bball ref
            html = urllib2.urlopen(url, timeout=5)
        
        soup = BeautifulSoup(html,"lxml")
        
        #get list of players 
        num_players = len(soup.select('tbody')[0].findAll('tr')) #number of players on page. 
        
        #loop through player list
        for players in np.arange(num_players):
            if int(soup.select('tbody')[0].findAll('tr')[players].findAll('td')[2].text) > 1979: #only get data from players after 3 point line
                players1+=1
                
                #print soup.select('tbody')[0].findAll('tr')[players].findAll('td')[0].findAll('a', href=True)[0]['href']
                #used this for debugging
                
                #get data off web
                url2 = basic_url+soup.select('tbody')[0].findAll('tr')[players].findAll('td')[0].findAll('a', href=True)[0]['href']

                try:
                    html2 = urllib2.urlopen(url2,timeout=5)
                except:
                    time.sleep(1)  #slow things down so bball ref doesn't get mad
                    html2 = urllib2.urlopen(url2, timeout=5)
                    
                soup2 = BeautifulSoup(html2,"lxml")
                
                #collect data from html
                name = [soup2.findAll('h1')[0].text]
                year = [convert_float(soup2.findAll('tbody')[2].findAll('tr')[0].select('td')[0].text[0:4])]
                age = [convert_float(soup2.findAll('tbody')[2].findAll('tr')[0].select('td')[1].text)]
                games = [convert_float(soup2.findAll('tfoot')[2].findAll('tr')[0].select('td')[5].text)]
                per36 = [convert_float(x.text) for x in soup2.findAll('tbody')[2].findAll('tr')[0].select('td')[5:]]
                RTG = [convert_float(x.text) for x in soup2.findAll('tbody')[3].findAll('tr')[0].select('td')[-2:]]
                adv = [convert_float(x.text) for i,x in enumerate(soup2.findAll('tbody')[4].findAll('tr')[0].select('td')[7:]) if i != 12 and i != 17]
                out = name+year+age+games+per36+RTG+adv
                
                #make dataframe
                if players1==1: #first player
                    df = pd.DataFrame(out).T
                else:
                    df = df.append(pd.Series(out),ignore_index=True)
    
    #create column headers
    name = ['Name']
    year = ['Year']
    age = ['age']
    games = ['Career Games']
    headers1 = [x.text for x in soup2.findAll('thead')[2].findAll('tr')[0].select('th')[5:]]
    headers2 = [x.text for x in soup2.findAll('thead')[3].findAll('tr')[0].select('th')[-2:]]
    headers3 = [x.text for x in soup2.findAll('thead')[4].findAll('tr')[0].select('th')[7:] if len(x.text)>0]
    headers = name+year+age+games+headers1+headers2+headers3
    df.columns = headers
    df.index = range(np.size(df,0))
    df = df.fillna(0)
    
    return df
