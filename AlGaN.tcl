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

#parameters for AlGaN high field mobility from Farahmand U=0 (hfalpha is Farahmand's alpha)
pdbSetDouble AlGaN Elec hfalpha 6.9502
pdbSetDouble AlGaN Elec n1 7.8138
pdbSetDouble AlGaN Elec n2 0.7897
pdbSetDouble AlGaN Elec Ecmob 245579.4
pdbSetDouble AlGaN vsat 2.02e7

#Farahmand high field parameters for U=deltaEc: hfalpha 3.2332, n1 5.3193, n2 1.0396,
#Ecmob 365552.9, vsat 1.1219e5 (low field mobility 213.1)

#mobModel (set in GaN_modelfile_masterD): static = constant mobility,
#field = Farahmand low field and high field mobility
if {$mobModel eq "field"} {
    set Tn "(Temp/300)"
    set N "(abs(Doping)+IonAcceptor+1.0)"
    set mumin [pdbGetDouble AlGaN Elec mumin]
    set mumax [pdbGetDouble AlGaN Elec mumax]
    set seg1 "$mumin*exp(log($Tn)*([pdbGetDouble AlGaN Elec beta1]))"
    set seg2 "($mumax-$mumin)*exp(log($Tn)*([pdbGetDouble AlGaN Elec beta2]))"
    set Nr "([pdbGetDouble AlGaN Elec Nref]*exp(log($Tn)*([pdbGetDouble AlGaN Elec beta3])))"
    set a "([pdbGetDouble AlGaN Elec alpha]*exp(log($Tn)*([pdbGetDouble AlGaN Elec beta4])))"
    pdbSetDouble AlGaN Elec lowfldmob "(($seg1)+($seg2)/(1+exp(log($N/$Nr)*$a)))"

    #Farahmand high field: mu = (mulow + vsat E^(n1-1)/Ec^n1) / (1 + hfalpha (E/Ec)^n2 + (E/Ec)^n1),
    #E along the channel (V/cm)
    set mulow "([pdbGetDouble AlGaN Elec lowfldmob])"
    set Ec [pdbGetDouble AlGaN Elec Ecmob]
    set n1 [pdbGetDouble AlGaN Elec n1]
    set r "((abs(dot(DevPsi,y*1e-4))+1)/$Ec)"
    set rn1m1 "exp(log($r)*($n1-1))"
    set num "($mulow+([pdbGetDouble AlGaN vsat]*$rn1m1/$Ec))"
    set den "(1.0+[pdbGetDouble AlGaN Elec hfalpha]*exp(log($r)*([pdbGetDouble AlGaN Elec n2]))+$rn1m1*$r)"
    pdbSetDouble AlGaN Elec mob "($num/$den)"
} else {
    pdbSetDouble AlGaN Elec mob 213.3
}

pdbSetDouble AlGaN Hole mob 0.2

pdbSetDouble AlGaN Thermalk 0.33
pdbSetDouble AlGaN Heatcap 2.0
