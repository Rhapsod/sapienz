The DEAP framework (https://github.com/DEAP/deap) is NOT part of Sapienz.
> Sapienz is implemented based on the DEAP framework.  

apktool.jar (http://ibotpeaches.github.io/Apktool/) is NOT part of Sapienz.  
> Sapienz uses apktool.jar for extracting static strings.  

motifcore.jar is part of Sapienz. 
> The motifcore of Sapienz implements hybrid exploration (systematic + fuzzing).  
> Its test generator initialises 'atomic' and 'motif' events and represents them  
> in a script that can be replicated by its replayer.  
> The implementation reuses Android Monkey for generating fuzzing events.  