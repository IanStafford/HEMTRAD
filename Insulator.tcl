mater add name=Nitride alias = nitride

pdbSetString Nitride YoungsModulus "(3.9e12-0.16e10*(Temp-300.0)) "
# We're not doing temp simluations so may remove this
pdbSetString Nitride PoissonRatio 0.352

#set Nitride electron effective mass
pdbSetDouble Nitride Elec me 0.2
#set Nitride hole effective mass
pdbSetDouble Nitride Hole mh 1.5

set me ([pdbDelayDouble Nitride Elec me])
set mh ([pdbDelayDouble Nitride Hole mh])

pdbSetDouble Nitride Elec Nc (2.50945e19*sqrt($me*$me*$me)*sqrt(Temp*Temp*Temp/2.7e7))
pdbSetDouble Nitride Hole Nv (2.50945e19*sqrt($mh*$mh*$mh)*sqrt(Temp*Temp*Temp/2.7e7))

#set Nitride electron affinity
pdbSetDouble Nitride Affinity 0.95

# Feel like its weird that I'm not using these values for the model?
pdbSetDouble Nitride Eg 5.4
pdbSetDouble Nitride DevPsi RelEps 6.3
pdbSetDouble Nitride Elec mob 1e-2
pdbSetDouble Nitride Hole mob 1e-3

#Set Ev and Ec using AlGaN Ei as zero
pdbSetDouble Nitride Hole Ev "((-[pdbGetDouble Nitride Affinity])-([pdbGetDouble Nitride Eg])+(DevPsi))"
pdbSetDouble Nitride Elec Ec "((-[pdbGetDouble Nitride Affinity])+(DevPsi))"

pdbSetDouble Nitride Thermalk 2.85
pdbSetDouble Nitride Heatcap 2.584

mater add name=Oxide    alias=oxide
    #set Oxide electron affinity
    pdbSetDouble Oxide Affinity 2.89

    pdbSetDouble Oxide DevPsi RelEps 3.9
    pdbSetDouble Oxide Eg 9.3
   
    #Set Ev and Ec using AlGaN Ei as zero
    pdbSetDouble Oxide Hole Ev "((-[pdbGetDouble Oxide Affinity])-([pdbGetDouble Oxide Eg])+(DevPsi))"
    pdbSetDouble Oxide Elec Ec "((-[pdbGetDouble Oxide Affinity])+(DevPsi))"

    pdbSetDouble Oxide Thermalk 2.85
    pdbSetDouble Oxide Heatcap 2.584

mater add name=HighK    alias=highk
    #set HighK electron affinity
    pdbSetDouble HighK Affinity 2.89

    pdbSetDouble HighK DevPsi RelEps 35
    pdbSetDouble HighK Eg 9.3

    #Set Ev and Ec using AlGaN Ei as zero
    pdbSetDouble HighK Hole Ev "((-[pdbGetDouble HighK Affinity])-([pdbGetDouble HighK Eg])+(DevPsi))"
    pdbSetDouble HighK Elec Ec "((-[pdbGetDouble HighK Affinity])+(DevPsi))"
