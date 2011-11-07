#!/usr/bin/env python
"""
    Program to convert number to words
    @author: Prashanth
    date: 09/08/11
"""

w1 = {
    '0':'Zero','1':'One','2':'Two','3':'Three','4':'Four','5':'Five','6':'Six','7':'Seven','8':'Eight','9':'Nine','10':'Ten','11':'Eleven','12':'Twelve','13':'Thirteen','14':'Fourteen','15':'Fifteen','16':'Sixteen','17':'Seventeen','18':'Eighteen','19':'Ninteen'
}
w2 = {
   '0':'','1':'Ten','2':'Twenty','3':'Thirty','4':'Fourty','5':'Fifty','6':'Sixty','7':'Seventy','8':'Eighty','9':'Ninty',
}

def remove_zeros(num):
    if num.startswith('0'):
        num = num[1:]
        return remove_zeros(num)
    else:
        return num

def get_word(n):
    n = remove_zeros(n)
    try:
        if len(n) == 1:
            return w1[n[0]]
        elif int(n) <= 19:
            return w1[n[0]+n[1]]
        elif int(n) > 19 and n[1] != '0':
            return '%s %s' % (w2[n[0]],w1[n[1]])
        elif int(n) > 19 and n[1] == '0':
            return '%s' % w2[n[0]]
        else:
            return ''
    except ValueError:
        return ''

def num2word(n):
    """
        Convert number to words 
    """
    n = remove_zeros(n)
    ns = str(n) # no string
    nw,nw1,nw2,nw3,nw4 = ('','','','','')
    nod = len(ns) # no of digits
    tens = ["ten ","eleven ","twelve ","thirteen ", "fourteen ",
        "fifteen ","sixteen ","seventeen ","eighteen ","nineteen "]
    twenties = ["","","twenty ","thirty ","forty ",
        "fifty ","sixty ","seventy ","eighty ","ninety "]
    #Process hundreds
    n1 = ns[-3:]
    if n1 and len(n1) < 3:
        nw1 = get_word(n1)
    elif int(n1)%100 == 0:
        nw1 = ' %s hundred' % w1[n1[0]]
    elif int(n1)%100 != 0:
        nw1 = ' %s hundred and %s' % (w1[n1[0]],get_word(n1[1]+n1[2]))
    #Process thousands
    n2 = ns[-5:-3]
    if n2:
        nw2 = '%s thousand' % get_word(n2)
    #Process Lakhs
    n3 = ns[-7:-5]
    if n3:
        nw3 = '%s lakh ' % get_word(n3)
    #Process Crore
    n4 = ns[-8:-7]
    if n4:
        nw4 = '%s crore ' % get_word(n4)
    nw = nw4+nw3+nw2+nw1
    nw = nw.replace('Zero hundred','')
    return nw

if __name__ == '__main__':
    n = raw_input('Enter a number:')
    #n = '78956101'
    #test
    #for i in range(1,101): 
    #    print num2word(i)
    print 'Number:%s' % n 
    print 'In words: %s' % num2word(n)
