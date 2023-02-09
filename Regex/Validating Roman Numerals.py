regex_pattern = r""	# Do not delete 'r'.

#thousand symbol is M, M can be in the first 4 positions of a numeral,hence the indices
thousand='M{0,3}'
#CM/CD OR D followed by C in the next 3 indices
hundred='(C[MD]|D?C{0,3})'
#XL/XC or L followed by X in next 3 indices
ten='(X[CL]|L?X{0,3})'
#IV/IX or V followed by I in next 3 indices
digit='(I[VX]|V?I{0,3})'

#%s is a placeholder for strings & the $ signifies the end of a string/line
regex_pattern=r"%s%s%s%s$" % (thousand, hundred, ten, digit)
