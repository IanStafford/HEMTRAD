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

    #paramters for GaN low field mobility from Farahmand
    pdbSetDouble GaN Elec mumin 295.0
    pdbSetDouble GaN Elec mumax 1907    ;#1460.7 before
    pdbSetDouble GaN Elec alpha 0.66
    pdbSetDouble GaN Elec beta1 -1.02
    pdbSetDouble GaN Elec beta2 -3.84
    pdbSetDouble GaN Elec beta3 3.02
    pdbSetDouble GaN Elec beta4 0.81
    pdbSetDouble GaN Elec Nref 1e17

    #parameters for GaN high field mobility from Farahmand (hfalpha is Farahmand's alpha)
    pdbSetDouble GaN Elec hfalpha 6.1973
    pdbSetDouble GaN Elec n1 7.2044
    pdbSetDouble GaN Elec n2 0.7857
    pdbSetDouble GaN Elec Ecmob 220893.6
    pdbSetDouble GaN vsat (2.7e7/(1+0.8*exp(Temp/600)))   ;# Farahmand 300 K value: 1.9064e7

    #parameters for GaN low field mobility using Eric Heller's equations
    set ericmob "(1630)/(exp(log(Temp/300)*(1.88)))"

    #mobModel (set in GaN_modelfile_masterD): static = constant mobility,
    #field = Farahmand low field mobility with Heller high field saturation
    if {$mobModel eq "field"} {
        set Tn "(Temp/300)"
        #ionized impurity density, including ionized acceptor traps
        set N "(abs(Doping)+IonAcceptor+1.0)"
        set mumin [pdbGetDouble GaN Elec mumin]
        set mumax [pdbGetDouble GaN Elec mumax]
        set seg1 "$mumin*exp(log($Tn)*([pdbGetDouble GaN Elec beta1]))"
        set seg2 "($mumax-$mumin)*exp(log($Tn)*([pdbGetDouble GaN Elec beta2]))"
        set Nr "([pdbGetDouble GaN Elec Nref]*exp(log($Tn)*([pdbGetDouble GaN Elec beta3])))"
        set a "([pdbGetDouble GaN Elec alpha]*exp(log($Tn)*([pdbGetDouble GaN Elec beta4])))"
        pdbSetDouble GaN Elec lowfldmob "(($seg1)+($seg2)/(1+exp(log($N/$Nr)*$a)))"

        #Heller high field: mu = mulow / (1 + (mulow E / vsat)^beta)^(1/beta), E along the channel (V/cm)
        set mulow "([pdbGetDouble GaN Elec lowfldmob])"
        set E "(abs(dot(DevPsi,y*1e-4))+1)"
        set vs "(3.3e7-(3.0e6*$Tn))"
        set b "(0.85*exp(log($Tn)*(0.4)))"
        pdbSetDouble GaN Elec mob "($mulow/exp(log(1+exp(log($mulow*$E/$vs)*$b))/$b))"
    } else {
        # set GaN mobility as a constant (Lu's results for 1um AFRL devices give 1907 cm2/V-s,
        # decreasing 41% to 1125 with 2e14 radiation)
        pdbSetDouble GaN Elec mob 600
    }

    #set hole mobility as constant
    pdbSetDouble GaN Hole mob 100
