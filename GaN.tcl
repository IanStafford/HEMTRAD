mater add name=GaN

	#Set Youngs Modulus and Poissons Ratio(for WZ crystal 0001 plane) plus temperature dependance ***check this number
	pdbSetString GaN YoungsModulus (3.9e12-0.16e10*(Temp-300.0))
	pdbSetString GaN PoissonRatio 0.352

    #set some GaN parameters
    pdbSetDouble GaN DevPsi RelEps 8.9
    
    #set GaN electron affinity
    
    pdbSetDouble GaN Affinity 3.1
	    
    #set Bandgap according to Eric Heller info
    pdbSetDouble GaN Eg (3.51-(7.7e-4*Temp*Temp)/(600+Temp))

    #set Ev and Ec for GaN 
    pdbSetDouble GaN Hole Ev "((-[pdbGetDouble GaN Affinity])-([pdbGetDouble GaN Eg])+(DevPsi))"
    pdbSetDouble GaN Elec Ec "((-[pdbGetDouble GaN Affinity])+(DevPsi))"

    pdbSetDouble GaN Hole Nv (4.6e19*sqrt(Temp*Temp*Temp/2.7e7))
    pdbSetDouble GaN Elec Nc (2.3e18*sqrt(Temp*Temp*Temp/2.7e7))

    #set low field electron mobility via analytical expression from Farahmand for low field mobility


    #paramters for GaN for low field mobility from Farahmand
    pdbSetDouble GaN Elec mumin 295.0
    pdbSetDouble GaN Elec mumax 1907    ;#1460.7 before
    pdbSetDouble GaN Elec alpha 0.66
    pdbSetDouble GaN Elec beta1 -1.02
    pdbSetDouble GaN Elec beta2 -3.84
    pdbSetDouble GaN Elec beta3 3.02
    pdbSetDouble GaN Elec beta4 0.81
    pdbSetDouble GaN Elec Nref 1e17 


    set Gmumin ([pdbGetDouble GaN Elec mumin])
    set Gmumax ([pdbGetDouble GaN Elec mumax])
    set Glowalpha ([pdbGetDouble GaN Elec alpha])
    set Gbeta1 ([pdbGetDouble GaN Elec beta1])
    set Gbeta2 ([pdbGetDouble GaN Elec beta2])
    set Gbeta3 ([pdbGetDouble GaN Elec beta3])
    set Gbeta4 ([pdbGetDouble GaN Elec beta4])
    set GNref ([pdbGetDouble GaN Elec Nref])
 
    #build equation for low field mobility
    set Gseg1 "$Gmumin*(1*exp(log(Temp/300)*($Gbeta1)))"
    set Gseg2 "($Gmumax-$Gmumin)*(1*exp(log(Temp/300)*($Gbeta2)))"
    set Gseg3 "$GNref*(1*exp(log(Temp/300)*($Gbeta3)))"
    set Gseg4 "abs((Doping+Acceptor+1)/$Gseg3)";     #modified to include ionized donor or acceptor traps
    set Gseg5 "$Glowalpha*(1*exp(log(Temp/300)*($Gbeta4)))"
    set Gseg6 "1*exp(log($Gseg4)*($Gseg5))"
    set Gseg7 "1+$Gseg6"
    set Gseg8 "($Gseg2)/($Gseg7)"

    #pdbSetDouble GaN Elec lowfldmob "($Gseg1+(($Gseg2)/($Gseg7)))"
    #pdbSetDouble GaN Elec lowfldmob $Gseg1+((($Gmumax-$Gmumin)*(exp(log(Temp/300)*($Gbeta2))))/($Gseg7))
    pdbSetDouble GaN Elec lowfldmob "($Gseg1)+($Gseg8)"



    #parameters for GaN low field mobility using Eric Heller's equations
    set top "1630"
    set bot1 "(Temp/300)"
    set bot2 "exp(log($bot1)*(1.88))"
    set ericmob "($top)/($bot2)"

    #pdbSetDouble GaN Elec lowfldmob $ericmob
   
    #pdbSetDouble GaN Elec mob $ericmob
   
    #parameters and expression for high field mobility using Eric Heller's equations
    set Gvsat "3.3e7-(3.0e6*(Temp/300))"
    set Gbeta "0.85*(exp(log(Temp/300)*(0.4)))"
    set GEfield "abs(dot(DevPsi,y*1e-4))+1"

    #set GEfield "(sqrt(dot(DevPsi,DevPsi)+1.0))"

    #set GEfield "(sqrt(dot(Qfn,Qfn)+1.0))"

    set G1 "((([pdbGetDouble GaN Elec lowfldmob])*($GEfield))/($Gvsat))"
    set G2 "(exp(log($G1)*($Gbeta)))"
    set G3 "(1+($G2))"
    set G4 "(1/$Gbeta)"
    set G5 "(exp(log($G3)*($G4)))"

    set Ghigh "(([pdbGetDouble GaN Elec lowfldmob])/($G5))"
      
    pdbSetDouble GaN Elec mob $Ghigh   ; # turn this one back on to get Farhamand mobility
   
    #set parameters for GaN High Field mobility from Farahmand 
    pdbSetDouble GaN Elec alpha 6.1973
    pdbSetDouble GaN Elec n1 7.2044
    pdbSetDouble GaN Elec n2 0.7857
    pdbSetDouble GaN Elec Ecmob 220893.6
    pdbSetDouble GaN vsat 1.9064e7 
    pdbSetDouble GaN vsat (2.7e7/(1+0.8*exp(Temp/600)))

    #set electron mobility via analytical expression from Farahmand for high field mobility

    set Glowfldmob ([pdbGetDouble GaN Elec lowfldmob]) 
    set Ghighalpha ([pdbGetDouble GaN Elec alpha])
    set Gn1 ([pdbGetDouble GaN Elec n1])
    set Gn2 ([pdbGetDouble GaN Elec n2])
    set GEcmob ([pdbGetDouble GaN Elec Ecmob])
    set Gvsat ([pdbGetDouble GaN vsat])
    set GEfield1 "abs(dot(DevPsi,y*1.e-4))+1"    

    set GEfield_EcRatio1 "(($GEfield1)/($GEcmob))"
    set GEn1_1 "(exp(log($GEfield1)*($Gn1-1)))"
    set GEn1_3 "(exp(log($GEcmob)*($Gn1)))"
    set GEn1_2 "(exp(log($GEfield_EcRatio1)*($Gn1)))"
    set GEn2_1 "(exp(log($GEfield_EcRatio1)*($Gn2)))"
    set num1 "($Glowfldmob+($Gvsat*(($GEn1_1)/($GEn1_3))))"
    set denom1 "(1.0+($Ghighalpha*($GEn2_1))+($GEn1_2))"

    #set testmob1 "($num1)/($denom1)"

# set GaN mobility as a constatn based on Lu's results for 1um AFRL devices 1907 cm2/V-s
    #pdbSetDouble GaN Elec mob 1907      ;# 1907,  decrease 41% with 2e14 radiation is 1125  
    pdbSetDouble GaN Elec mob 600

    #set hole mobility as constant
    pdbSetDouble GaN Hole mob 100

