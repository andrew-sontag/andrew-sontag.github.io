#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author:    Andrew Sontag
Created:   Mon Apr 10 22:57:05 2023
"""
import numpy as np
#import matplotlib.pyplot as plt
import sys
import pdb
from collections import Counter

#DO NOT USE: ^, @, +, -, *, D
# "units" are phrased as powers of energy, setting hbar=c=1

#Define all of your vectors, scalars, and indices here.

# Vectors:
vecs = ['p1', 'p2', 'k']
vecsunits = [1, 1, 1]

# Scalars: (do not need to include "p.k")
scas = ['x', 'y', 'mh^2', '1/mw^2']
scasunits = [0, 0, 2, -2]

#Metric
eta = 'eta'

#Indices
inds = ['a', 'b', 'c', 'd', 'e', 'm', 'n']

#Objects are lists of monomials.
#Each monomial is a list of vecs, scas, and etas multiplied together.
#Indices on vecs are denoted by:  vec@ind

for i, vec1 in enumerate(vecs):
    for vec2 in vecs[i:]:
        if vec1 == vec2:
            tmp = vec1+'^2'
        else:
            tmp = vec1+'.'+vec2
        if not tmp in scas:
            scas.append(tmp)
            scasunits.append(2)
if 'D' in scas:
    print('Warning! You put D in scalars! We will interpret this to be "Dimension"')
else:
    scas.append('D')
    scasunits.append(0)


            
def contract(mon, stop=False):
    """This function finds all pairs of Lorentz indices and contracts them into appropriate scalars."""
    # Can feed any monomial within an object, output monomial needs to be consolidated.
    if stop:
        pdb.set_trace()
    if type(mon[0]) is list:
        print('Something went wrong!')
        sys.exit()
    indlist = [-1 for item in mon]
    etalist = []
    outlist = []
    for i, item in enumerate(mon):
        if not type(item) is str:
            continue
        if item[:len(eta)] == eta:
            indlist[i] = -2
            tmp = item.split('@')
            tmplist = []
            if not len(tmp) == 3:
                print('Mislabeled Index Catch 1')
                sys.exit()
            for piece in tmp[1:]:
                if piece in inds:
                    tmplist.append(inds.index(piece))
                else:
                    print('Mislabeled Index Catch 2')
                    sys.exit()
            etalist.append([ i for i in tmplist])
        elif '@' in item:
            tmp = item.split('@')
            if not len(tmp) == 2:
                print('Mislabeled Index Catch 3')
                sys.exit()
            if tmp[-1] in inds:
                indlist[i] = inds.index(tmp[-1])
            else:
                print('Mislabeled Index Catch 4')
                sys.exit()
    done = False
    for count in range(1000):
        if done:
            break
        repeat = True
        etalist2 = [e for e in etalist]
        for k, pair in enumerate(etalist):
            for l in range(len(etalist)):
                if l <= k:
                    continue
                elif etalist2[l] == 0:
                    print('???')
                    sys.exit()
                if pair[0] == etalist2[l][0]:
                    etalist2[k]=0
                    etalist2[l][0] = pair[1]
                    repeat = False
                    break
                elif pair[0] == etalist2[l][1]:
                    etalist2[k]=0
                    etalist2[l][1] = pair[1]
                    repeat = False
                    break
                elif pair[1] == etalist2[l][0]:
                    etalist2[k]=0
                    etalist2[l][0] = pair[0]
                    repeat = False
                    break
                elif pair[1] == etalist2[l][1]:
                    etalist2[k]=0
                    etalist2[l][1] = pair[0]
                    repeat = False
                    break
            if not repeat:
                break
        for m, pair in enumerate(etalist2):
            if (not pair is 0) and pair[0] == pair[1]:
                etalist2[m] = 0
                outlist.append('D')
        etalist = [e for e in etalist2 if not e is 0]
        if repeat:
            done = True
    if not done:
        print('Big Problem')
        sys.exit()
    for pair in etalist:
        if pair[0] in indlist:
            if indlist.count(pair[0])>1:
                print('Mislabeled Index Catch 5')
                sys.exit()
            indlist[indlist.index(pair[0])] = pair[1]
        elif pair[1] in indlist:
            if indlist.count(pair[1])>1:
                print('Mislabeled Index Catch 6')
                sys.exit()
            indlist[indlist.index(pair[1])] = pair[0]
        else:
            outlist.append(eta+'@'+inds[pair[0]]+'@'+inds[pair[1]])
    for j, ind in enumerate(indlist):
        if ind == -1:
            outlist.append(mon[j])
        elif ind == -2 or ind == -3:
            continue
        elif j < len(indlist)-1:
            if ind in indlist[j+1:]:
                if indlist.count(ind)>2:
                    print('Mislabeled Index Catch 7')
                    sys.exit()
                if mon[j].split('@')[0] == mon[indlist.index(ind, j+1)].split('@')[0]:
                    tmp = mon[j].split('@')[0]+'^2'
                    if tmp in scas:
                        outlist.append(tmp)
                        indlist[indlist.index(ind, j+1)] = -3
                else:
                    tmp = mon[j].split('@')[0]+'.'+mon[indlist.index(ind, j+1)].split('@')[0]
                    if tmp in scas:
                        outlist.append(tmp)
                        indlist[indlist.index(ind, j+1)] = -3
                    else:
                        tmp = mon[indlist.index(ind, j+1)].split('@')[0]+'.'+mon[j].split('@')[0]
                        if tmp in scas:
                            outlist.append(tmp)
                            indlist[indlist.index(ind, j+1)] = -3
                        else:
                            print('Mislabeled Index Catch 8')
                            sys.exit()
            elif ind > -2:
                if ind == -1:
                    outlist.append(mon[j])
                else:
                    outlist.append(mon[j].split('@')[0]+'@'+inds[ind])
        elif ind > -2:
            if ind == -1:
                outlist.append(mon[j])
            else:
                outlist.append(mon[j].split('@')[0]+'@'+inds[ind])
    return(outlist)
    
    
    
def consolidate(obj):
    """This function "combines like terms" added within an object."""
    # Can feed any object, output is consolidated (does not effect contraction).
    ret0 = [r for r in obj]
    for i, mon in enumerate(ret0):
        for j, item in enumerate(mon):
            if (type(item) is str) and (item[:len(eta)] == eta):
                twoinds = item.split('@')[1:]
                sortwoinds = sorted(twoinds)
                ret0[i][j] = eta+'@'+sortwoinds[0]+'@'+sortwoinds[1]
    ret = []
    for mon in ret0:
        tmp = [i for i in mon if not type(i) is str]
        tmp2 = [i for i in mon if type(i) is str]
        if len(tmp)==0:
            ret.append([1]+mon)
        else:
            ret.append([np.prod(tmp)]+tmp2)
    ret2 = [r for r in ret]
    for i in range(len(ret)):
        for j in range(len(ret)):
            if ret2[i] is 0:
                break
            if j<=i:
                continue
            elif len(ret2[i]) == 1 and len(ret2[j]) == 1:
                ret2[j][0] = ret2[i][0]+ret2[j][0]
                ret2[i] = 0
                continue
            elif len(ret2[i]) == 1 or len(ret2[j]) == 1:
                continue
            elif Counter(ret2[i][1:]) == Counter(ret2[j][1:]):
                ret2[j][0] = ret2[i][0]+ret2[j][0]
                ret2[i] = 0
                continue
    ret2 = [i for i in ret2 if ((not i is 0) and (not i[0]==0))]
    return(ret2)
    


def multiply(obj1, obj2):
    """This function multiplies two objects together."""
    # MUST feed contracted objects, output needs to be consolidated and recontracted
    ret = []
    for mon1 in obj1:
        for mon2 in obj2:
            ret.append(mon1+mon2)
    return(ret)
    
    

def powers(obj):
    """This function "combines like terms" multiplied within monomials in an object."""
    # Can feed any object, output will remain consolidated and contracted
    ret = []
    for mon in obj:
        monret = []
        tbd_things = []
        tbd_powers = []
        tbd_units = []
        for j, item in enumerate(mon):
            if (type(item) is str) and ('^' in item):
                tmp = item.split('^')
                if not int(tmp[1])==float(tmp[1]):
                    print('Sorry! No noninteger powers are supported yet.')
                    sys.exit()
                if tmp[0] in tbd_things:
                    tbd_powers[tbd_things.index(tmp[0])] += int(tmp[1])
                else:
                    tbd_things.append(tmp[0])
                    tbd_powers.append(int(tmp[1]))
                    tbd_units.append(scasunits[scas.index(item)] // int(tmp[1]))
            elif (type(item) is str) and (item in scas):
                if (item in tbd_things):
                    tbd_powers[tbd_things.index(item)] += 1
                elif (j<len(mon)-1) and (item in mon[j+1:]):
                    tbd_things.append(item)
                    tbd_powers.append(1)
                    tbd_units.append(scasunits[scas.index(item)])
                else:
                    monret.append(item)

            else:
                monret.append(item)
        for i in range(len(tbd_things)):
            tmp = tbd_things[i]+'^'+str(tbd_powers[i])
            monret.append(tmp)
            if not tmp in scas:
                scas.append(tmp)
                scasunits.append(tbd_powers[i]*tbd_units[i])
        ret.append(monret)
    return(ret)
    


def countks(sortmon, k='k'):
    """This function counts the power of argument "k" in a monomial."""
    count = 0
    for item in sortmon[2]:
        if k in item:
            if '^' in item:
                count += item.split('^')[0].count(k) * int(item.split('^')[1])
            else:
                count += item.count(k)
    return(count)
    


    
def nice_output(obj):
    """This function takes an object and returns a string fit for human reading."""
    # MUST be fed a contracted, consolidated, powered object
    sortobj = []
    for mon in obj:
        if len(mon)==1:
            sortobj.append(mon)
        else:
            sortind = [i for i in mon[1:] if ((type(i) is str) and ('@' in i))]
            sortelse = [i for i in mon[1:] if not ((type(i) is str) and ('@' in i))]
            sortobj.append([mon[0], sorted(sortind), sorted(sortelse)])
    sortedobj = sorted(sortobj, key = lambda x:(str(x[1]), -1*countks(x)) )
    ret = ''
    tmp = []
    for monl in sortedobj:
        if not monl[1] == tmp:
            tmp = monl[1]
            if len(ret)>0:
                ret += ')   +   '
            ret += '('
            for item in tmp:
                tmpp = item.split('@')
                ret += tmpp[0]
                for ind in tmpp[1:]:
                    ret += '_'+ind
                ret += ' '
            ret = ret[:-1]+ ')('
        else:
            if len(ret)>0:
                ret += '  +  '
            else:
                ret += '('
        if monl[0] == int(monl[0]):
            ret += str(int(monl[0]))
        else:
            ret += str(monl[0])
        for item in monl[2]:
            ret += ' '+item
    ret += ')'
    return(ret)
    
    
    
def clean(obj):
    """This function consolidates, contracts, reconsolidates, and powers an object."""
    obj1 = consolidate(obj)
    obj1 = [contract(mon) for mon in obj1]
    return(powers(consolidate(obj1)))
    
    
    
def exponent(obj, power):
    """This function raises an entire object to an integer power."""
    tmp = clean(obj)
    for i in range(power-1):
        tmp = clean(multiply(obj, tmp))
    return(tmp)
    
    
    
def reindex(obj, ind1, ind2):
    """This function changes all instances of index "ind1" in object "obj" to "ind2." """
    ret = []
    for mon in obj:
        retm = []
        for item in mon:
            if (type(item) is str) and ('@' in item) and (ind1 in item.split('@')[1:]):
                reit = item.split('@')[0]
                for piece in item.split('@')[1:]:
                    if piece == ind1:
                        reit += '@'+ind2
                    else:
                        reit += '@'+piece
                retm.append(reit)
            else:
                retm.append(item)
        ret.append(retm)
    return(ret)
    
    
def insert(obj, item, rep_obj):
    """This function replaces every instance of "item" in object "obj" with object "rep_obj." """
    # "rep_obj" must be pre-contracted, and cannot have more than 1 index
    ret_obj = []
    if item in scas:
        for mon in obj:
            if item in mon:
                count = mon.count(item)
                tmp = [i for i in mon if not i==item]
                tmpo = clean(multiply([tmp], exponent(rep_obj, count)))
                ret_obj += tmpo
            else:
                ret_obj.append(mon)
    elif item in vecs:
        # Rep_obj needs to be pre-contracted, so it must have a single index (no etas)
        ind1 = False
        for repmon in rep_obj:
            seenyet = False
            for repitem in repmon:
                if (type(repitem) is str) and ('@' in repitem):
                    if ind1 is False:
                        ind1 = repitem.split('@')[1]
                        seenyet = True
                    elif seenyet:
                        print('Too many indices in one monomial')
                        sys.exit()
                    elif ind1 == repitem.split('@')[1]:
                        seenyet = True
                    else:
                        print('Two different indices')
                        sys.exit()
        if ind1 is False:
            print('Not enough indices')
            sys.exit()
        for mon in obj:
            count = []
            retmon = [[]]
            for thing in mon:
                if (type(thing) is str) and ('@' in thing) and (thing.split('@')[0] == item):
                     count.append( thing.split('@')[1] )
                else:
                     retmon[0].append(thing)
            for ind2 in count:
                retmon =  clean(multiply(retmon, reindex(rep_obj, ind1, ind2)))
            ret_obj += retmon
    else:
        print('Sorry, can only replace a given scalar or vector!')
        sys.exit()
    return(ret_obj)
    
    
def kshift(obj, newk, k='k'):
    """This function shifts vector "k" to some other vector "newk", taking into account scalars like k^2."""
    # Obj and newk must be appropriately cleaned and contracted NOTE newk is obj, not mon
    vecshift = clean(insert(obj, k, newk))
    for sca in scas:
        if sca[:len(k)+1] == k+'^':
            if int(sca[len(k)+1:])%2 != 0:
                print('Sorry, no odd powers of k in kshift')
                sys.exit()
            else:
                exp = int(sca[len(k)+1:])
                scashift = clean(exponent(multiply(newk, newk), exp//2))
                vecshift = clean(insert(vecshift, sca, scashift))
    return(vecshift)
    
    
def dropoddk(obj, k='k'):
    """This function removes all monomials containing odd powers of "k" from object "obj." """
    retobj = []
    for mon in obj:
        count = 0
        for item in mon:
            if (type(item) is str) and (k in item):
                if item[:len(k)+1] == k+'^':
                    if float(item[len(k)+1:]) == int(item[len(k)+1:]):
                        count += int(item[len(k)+1:])
                    else:
                        print('Sorry, no odd powers of k in dropoddk')
                        sys.exit()
                elif item[:len(k)+1] == k+'@':
                    count += 1
                elif ('.' in item) and item.count(k)==1:
                    if '^' in item:
                        if float(item.split('^')[-1]) == int(item.split('^')[-1]):
                            count += int(item.split('^')[-1])
                    else:
                        count += 1
                else:
                    print('Confused')
                    sys.exit()
        if count%2 == 0:
            retobj.append(mon)
    return(retobj)
    
    
    
def unitcheck(obj):
    """This function ensures that every monomial in object "obj" has the same units."""
    totunits = None
    for mon in obj:
        units = 0
        for item in mon:
            if item in vecs:
                units += vecsunits[vecs.index(item)]
            elif item in scas:
                units += scasunits[scas.index(item)]
            elif (type(item) is str):
                if '@' in item:
                    if item.split('@')[0] in vecs:
                        units += vecsunits[vecs.index(item.split('@')[0])]
                    elif not item.split('@')[0] == eta:
                        print('What the fuck is this:', item)
                        sys.exit()
                else:
                    print('What the fuck is this:', item)
                    sys.exit()
        if totunits is None:
            totunits = units
        elif totunits != units:
#            pdb.set_trace()
            print('This Term is Incorrect:  ', mon)
    return
        


###############################################################################
# Everything from here on is my own scratchwork for whatever latest problem
# I was working on. I leave it as a makeshift example.
###############################################################################

print('Running...\n\n\n')

t0ab = clean(multiply( clean([['k@a'], ['p1@a']]), clean([['k@b'], ['p1@b']]) ))
t1ab = clean([['eta@a@b']] + clean(multiply(t0ab, [[-1, '1/mw^2']])))

v0bcm = clean(multiply(clean([['eta@b@c']]), clean([[-2, 'k@m'], [-1, 'p1@m']])) + multiply(clean([['eta@b@m']]), clean([[+1, 'k@c'], [+2, 'p1@c']])) + multiply(clean([['eta@m@c']]), clean([[+1, 'k@b'], [-1, 'p1@b']])))

t0cd = clean(multiply( clean([['k@c']]), clean([['k@d']]) ))
t1cd = clean([['eta@c@d']] + clean(multiply(t0cd, [[-1, '1/mw^2']])))

v0den = clean(multiply(clean([['eta@d@e']]), clean([[-2, 'k@n'], [+1, 'p2@n']])) + multiply(clean([['eta@e@n']]), clean([[+1, 'k@d'], [-2, 'p2@d']])) + multiply(clean([['eta@d@n']]), clean([[+1, 'k@e'], [+1, 'p2@e']])))

t0ea = clean(multiply( clean([['k@e'], [-1, 'p2@e']]), clean([['k@a'], [-1, 'p2@a']]) ))
t1ea = clean([['eta@e@a']] + clean(multiply(t0ea, [[-1, '1/mw^2']])))

v0bemn = clean([[+1, 'eta@b@m', 'eta@e@n'], [+1, 'eta@e@m', 'eta@b@n'], [-2, 'eta@b@e', 'eta@m@n']])


T1 = clean(multiply(t1ab, v0bcm))
T2 = clean(multiply(t1cd, v0den))
T3 = clean(multiply(T1, T2))
T4 = clean(multiply(T3, t1ea))
T4n = multiply(T4, [[+1, '1/mw^2']])

X1 = clean(multiply(t1ab, v0bemn))
X2 = clean(multiply(X1, t1ea))
X3 = clean(multiply(X2, [[+0.5, 'k^2', '1/mw^2'], [-0.5]]))

Y4 = clean(T4n + X3)
#Note that addition works like addition should! I'm cute like that.

T40 = clean(insert(Y4, 'p1^2', [[0]]))
T41 = clean(insert(T40, 'p2^2', [[0]]))
T42 = clean(insert(T41, 'p1.p2', [[0.5, 'mh^2']]))

kins = [[1, 'k@a'], [-1, 'x', 'p1@a'], [+1, 'y', 'p2@a']]
T5 = kshift(T42, kins)
T6 = clean(insert(T5, 'p1^2', [[0]]))
T7 = clean(insert(T6, 'p2^2', [[0]]))
T8 = clean(insert(T7, 'p1.p2', [[0.5, 'mh^2']]))
T60 = clean(insert(T8, 'p1^4', [[0]]))
T70 = clean(insert(T60, 'p2^4', [[0]]))
T80 = clean(insert(T70, 'p1.p2^2', [[0.25, 'mh^4']]))
T9 = dropoddk(T80)

print(nice_output(T9))

            

        