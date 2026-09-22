mater add name=AlGaN

#define the parameters for AlGaN - all depend on a AlN_Ratio being set as a spatial variable
pdbSetDouble AlGaN DevPsi RelEps 9.0

#Set Youngs Modulus and Poissons Ratio(approximation from Nanoindentation in AlGaN paper, Caceres '99)
#pdbSetString AlGaN YoungsModulus (3.9e12+(5.555e11*AlN_Ratio)-0.16e10*(Temp-300.0))
pdbSetString AlGaN PoissonRatio 0.352

#set AlGaN electron affinity
pdbSetDouble AlGaN Affinity "((2.02275*(1-AlN_Ratio))+1.07725)"

#set AlGaN bandgap
pdbSetDouble AlGaN Eg "(6.13*AlN_Ratio+[pdbDelayDouble GaN Eg]*(1-AlN_Ratio)-1.0*AlN_Ratio*(1-AlN_Ratio))"

#Set Ev and Ec using AlGaN Ei as zero
pdbSetDouble AlGaN Hole Ev "((-[pdbGetDouble AlGaN Affinity])-([pdbGetDouble AlGaN Eg])+(DevPsi))"
pdbSetDouble AlGaN Elec Ec "((-[pdbGetDouble AlGaN Affinity])+(DevPsi))"

#copied from Full deck, don't know where the constants come from
pdbSetDouble AlGaN Elec me "((0.4*AlN_Ratio+0.20*(1-AlN_Ratio)))"
pdbSetDouble AlGaN Hole mh "((1.5*AlN_Ratio+3.53*(1-AlN_Ratio)))"

set me ([pdbDelayDouble AlGaN Elec me])
set mh ([pdbDelayDouble AlGaN Hole mh])
pdbSetDouble AlGaN Elec Nc (2.50945e19*sqrt($me*$me*$me)*sqrt(Temp*Temp*Temp/2.7e7))
pdbSetDouble AlGaN Hole Nv (2.50945e19*sqrt($mh*$mh*$mh)*sqrt(Temp*Temp*Temp/2.7e7))

#parameters for AlGaN low field mobility U=0
pdbSetDouble AlGaN Elec mumin 312.1
pdbSetDouble AlGaN Elec mumax 1401.3
pdbSetDouble AlGaN Elec alpha 0.74
pdbSetDouble AlGaN Elec beta1 -6.51
pdbSetDouble AlGaN Elec beta2 -2.31
pdbSetDouble AlGaN Elec beta3 7.07
pdbSetDouble AlGaN Elec beta4 -0.86
pdbSetDouble AlGaN Elec Nref 1e17


set Amumin ([pdbGetDouble AlGaN Elec mumin])
set Amumax ([pdbGetDouble AlGaN Elec mumax])
set Alowalpha ([pdbGetDouble AlGaN Elec alpha])
set Abeta1 ([pdbGetDouble AlGaN Elec beta1])
set Abeta2 ([pdbGetDouble AlGaN Elec beta2])
set Abeta3 ([pdbGetDouble AlGaN Elec beta3])
set Abeta4 ([pdbGetDouble AlGaN Elec beta4])
set ANref ([pdbGetDouble AlGaN Elec Nref])

#build equation for low field mobility
set Aseg1 "$Amumin*(exp(log(Temp/300)*($Abeta1)))"
set Aseg2 "($Amumax-$Amumin)*(exp(log(Temp/300)*($Abeta2)))"
set Aseg3 "$ANref*(exp(log(Temp/300)*($Abeta3)))"
#set Aseg4 "abs((Doping+Acceptor+1)/$Aseg3)"
set Aseg4 "(abs(Doping)+abs(Acceptor)+1)/$Aseg3)"
set Aseg5 "$Alowalpha*(exp(log(Temp/300)*($Abeta4)))"
set Aseg6 "exp(log($Aseg4)*($Aseg5))"
set Aseg7 "1+$Aseg6"

pdbSetDouble AlGaN Elec lowfldmob "($Aseg1+(($Aseg2)/($Aseg7)))"

#set electron mobility via analytical expression from Farahmand for high field mobility U=0
#pdbSetDouble AlGaN Elec lowfldmob 213.1
pdbSetDouble AlGaN Elec alpha 6.9502
pdbSetDouble AlGaN Elec n1 7.8138
pdbSetDouble AlGaN Elec n2 0.7897
pdbSetDouble AlGaN Elec Ecmob 245579.4
pdbSetDouble AlGaN vsat 2.02e7 
#pdbSetDouble AlGel N vsat ((2.5e7*AlN_Ratio)+(1.4e7*(1-AlN_Ratio)))

#set electron mobility via analytical expression from Farahmand for high field mobility U=deltaEc
#pdbSetDouble AlGaN Elec lowfldmob 213.1
#pdbSetDouble AlGaN Elec alpha 3.2332
#pdbSetDouble AlGaN Elec n1 5.3193
#pdbSetDouble AlGaN Elec n2 1.0396
#pdbSetDouble AlGaN Elec Ecmob 365552.9
#pdbSetDouble AlGaN vsat 1.1219e5 
#pdbSetDouble AlGaN vsat ((2.5e7*AlN_Ratio)+(1.4e7*(1-AlN_Ratio)))

set Alowfldmob ([pdbGetDouble AlGaN Elec lowfldmob]) 
set Ahighalpha ([pdbGetDouble AlGaN Elec alpha])
set An1 ([pdbGetDouble AlGaN Elec n1])
set An2 ([pdbGetDouble AlGaN Elec n2])
set AEcmob ([pdbGetDouble AlGaN Elec Ecmob])
set Avsat ([pdbGetDouble AlGaN vsat])
set AEfield "(sqrt(dot(DevPsi,DevPsi)+1.0e2))"
set AEfield_EcRatio "($AEfield)/($AEcmob)"

set AEn1 "exp(log($AEfield_EcRatio)*($An1-1))"
set AEn2 "exp(log($AEfield_EcRatio)*($An2))"

set Anum "($Alowfldmob+($Avsat*($AEn1)/($AEcmob)))"
set Aden "(1.0+($Ahighalpha*($AEn2))+($AEn1*$AEfield_EcRatio))"

#pdbSetDouble AlGaN Elec mob $Alowfldmob

#pdbSetDouble AlGaN Elec mob "($Anum)/($Aden)"
pdbSetDouble AlGaN Elec mob 213.3

pdbSetDouble AlGaN Hole mob 0.2

pdbSetDouble AlGaN Temp Abs.Error 0.1
pdbSetDouble AlGaN Temp Rel.Error 1.0e-2
pdbSetDouble AlGaN Temp DampValue 10.0

pdbSetDouble AlGaN Thermalk 0.33
pdbSetDouble AlGaN Heatcap 2.0

set eqn "((([pdbGetDouble AlGaN Heatcap]) * ddt(Temp))) - (([pdbGetDouble AlGaN Thermalk]) * (grad(Temp))) - ($q * [pdbGetDouble AlGaN Elec mob] * (Elec) * dot(Qfn,Qfn))"
pdbSetString AlGaN Temp Equation $eqn

