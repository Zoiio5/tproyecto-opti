% Modelo MiniZinc para Red de Tuberías - Grupo 5 (Optimizado para OR-Tools CP-SAT)
% Diámetros: D2=75mm, D3=100mm, D5=150mm | Costos: tipo a, tipo b
% -----------------------------------------------------------
% Escalamos todos los flujos (l/min → centilitros/min) y costos 
% (unidad monetaria → centicentavos) con factor SCALE = 100
% -----------------------------------------------------------

int: SCALE = 100;                % factor de escala (100 → 2 decimales)

% 1. Parámetros de tamaño y nodos
int: nP;                        
int: nT;                        
int: nC1;                       
int: nC2;                       
int: N = nP + nT + nC1 + nC2;   

set of int: P  = 1..nP;                   
set of int: T  = nP+1 .. nP+nT;           
set of int: C1 = nP+nT+1 .. nP+nT+nC1;     
set of int: C2 = nP+nT+nC1+1 .. N;         

% 2. Arcos de la red
int: nA;                                  
array[1..nA] of int: arc_from;            
array[1..nA] of int: arc_to;              

% 3. Demandas de los nodos (se escalan)
array[1..N] of float: demand;             
array[1..N] of int: demand_c = [ round(demand[i]*SCALE) | i in 1..N ];

% 4. Diámetros disponibles
int: nD = 3;                                          
array[1..nD] of int: diam_mm = [75,100,150];       
array[1..nD] of float: capacity = [795.0,1414.0,3181.0];
array[1..nD] of int: capacity_c = [ round(capacity[d]*SCALE) | d in 1..nD ];

% 5. Costos de instalación y transporte (se escalan)
array[1..nD] of float: cost_type_a = [20.0,24.0,32.0];
array[1..nD] of float: cost_type_b = [50.0,62.0,78.0];

array[1..nA,1..nD] of float: install_cost;  
array[1..nA] of float: trans_cost;

array[1..nA,1..nD] of int: install_cost_c = 
    array2d(1..nA,1..nD, [ round(install_cost[a,d]*SCALE) | a in 1..nA, d in 1..nD ]);

array[1..nA] of int: trans_cost_c = 
    [ round(trans_cost[a]*SCALE) | a in 1..nA ];

% 6. Variables de decisión (enteras/booleanas)
array[1..nA,1..nD] of var bool: y;      % diámetro instalado
array[1..nA] of var int: f_c;           % flujo escalado en centilitros/min
array[1..nA] of var bool: active;       

% 7. Restricciones
constraint forall(a in 1..nA) (
    active[a] <-> (f_c[a] > 0)
);

constraint forall(a in 1..nA) (
    sum(d in 1..nD)(bool2int(y[a,d])) = bool2int(active[a])
);

constraint forall(a in 1..nA) (
    f_c[a] <= sum(d in 1..nD)(capacity_c[d] * bool2int(y[a,d]))
);

constraint forall(i in T) (
    sum(a in 1..nA where arc_to[a]=i)(f_c[a]) =
    sum(a in 1..nA where arc_from[a]=i)(f_c[a])
);

constraint forall(i in C1) (
    sum(a in 1..nA where arc_to[a]=i)(f_c[a]) =
    demand_c[i] + sum(a in 1..nA where arc_from[a]=i)(f_c[a])
);

constraint forall(i in C2) (
    sum(a in 1..nA where arc_to[a]=i)(f_c[a]) =
    demand_c[i]
);

constraint forall(a in 1..nA)( f_c[a] >= 0 );

constraint
  sum(i in P, a in 1..nA where arc_from[a]=i)(f_c[a]) >=
  sum(i in C1 union C2)(demand_c[i]);

constraint forall(a in 1..nA) (
  (sum(d in 1..nD)(bool2int(y[a,d])) = 0) -> f_c[a]=0
);

% 8. Objetivo (enteros)
var int: total_install_cost_c =
    sum(a in 1..nA, d in 1..nD)( install_cost_c[a,d] * bool2int(y[a,d]) );

var int: total_transport_cost_c =
    sum(a in 1..nA)( trans_cost_c[a] * f_c[a] );

var int: total_cost_c = total_install_cost_c + total_transport_cost_c;

solve minimize total_cost_c;

% 9. Salida (convertimos de vuelta a reales)
output [
  "=== RESULTADOS OPTIMIZACIÓN RED DE TUBERÍAS - GRUPO 5 (CP-SAT) ===\n",
  "Costo Instalación: $", show(total_install_cost_c div SCALE), ".",
                     show(total_install_cost_c mod SCALE), "\n",
  "Costo Transporte:   $", show(total_transport_cost_c div SCALE), ".",
                     show(total_transport_cost_c mod SCALE), "\n",
  "COSTO TOTAL:        $", show(total_cost_c div SCALE), ".",
                     show(total_cost_c mod SCALE), "\n\n",
  "Arcos activos: ", show(sum(a in 1..nA)(bool2int(active[a]))), "/", show(nA), "\n",
  "Flujo total:   ", show(sum(i in P, a in 1..nA where arc_from[a]=i)(f_c[a]) / SCALE), " l/min\n",
  "Demanda total: ", show(sum(i in C1 union C2)(demand_c[i]) / SCALE), " l/min\n"
];
