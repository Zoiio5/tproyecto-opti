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

% 3. Suministro y demandas de los nodos (desde archivo .dzn)
array[1..N] of float: supply;
array[1..N] of float: demand;

% 4. Diámetros disponibles (desde archivo .dzn)
int: nD;                                          
array[1..nD] of int: diam_mm = [75,100,150];       
array[1..nD] of int: max_capacity;  % Viene del archivo .dzn
array[1..nD] of int: capacity_c = [ max_capacity[d]*SCALE | d in 1..nD ];

% 5. Costos de instalación y transporte (desde archivo .dzn, se escalan)
array[1..nA,1..nD] of float: install_cost;  
array[1..nA] of float: trans_cost;

array[1..nA,1..nD] of int: install_cost_c = 
    array2d(1..nA,1..nD, [ round(install_cost[a,d]*SCALE) | a in 1..nA, d in 1..nD ]);

array[1..nA] of int: trans_cost_c = 
    [ round(trans_cost[a]*SCALE) | a in 1..nA ];

% 6. Parámetros adicionales para reportes (con valores por defecto)
string: instance_size = "pequena";  % "pequeñas", "medianas", "grandes"
int: instance_number = 1;           % número de instancia
int: grupo = 5;

% 7. Variables de decisión (enteras/booleanas)
array[1..nA,1..nD] of var bool: y;      % diámetro instalado
array[1..nA] of var 0..1000000: f_c;    % flujo escalado en centilitros/min
array[1..nA] of var bool: active;       

% Variables auxiliares para nodos sin conexión
array[1..N] of var 0..100000: unmet_demand_c;

% 8. Restricciones principales
constraint forall(a in 1..nA) (
    active[a] <-> (f_c[a] > 0)
);

constraint forall(a in 1..nA) (
    sum(d in 1..nD)(bool2int(y[a,d])) <= 1  % Máximo un diámetro por arco
);

constraint forall(a in 1..nA) (
    f_c[a] <= sum(d in 1..nD)(capacity_c[d] * bool2int(y[a,d]))
);

% Balance de flujo para plantas (pueden producir hasta su capacidad)
constraint forall(i in P) (
    sum(a in 1..nA where arc_from[a]=i)(f_c[a]) <= round(supply[i]*SCALE)
);

% Balance de flujo para tanques de tránsito (balance perfecto)
constraint forall(i in T) (
    sum(a in 1..nA where arc_to[a]=i)(f_c[a]) =
    sum(a in 1..nA where arc_from[a]=i)(f_c[a])
);

% Balance de flujo para consumidores (permitir demanda no satisfecha)
constraint forall(i in C1 union C2) (
    sum(a in 1..nA where arc_to[a]=i)(f_c[a]) + unmet_demand_c[i] = 
    round(demand[i]*SCALE) + sum(a in 1..nA where arc_from[a]=i)(f_c[a])
);

% Los nodos no consumidores no tienen demanda no satisfecha
constraint forall(i in P union T) (
    unmet_demand_c[i] = 0
);

constraint forall(a in 1..nA)( f_c[a] >= 0 );

constraint forall(a in 1..nA) (
  if sum(d in 1..nD)(bool2int(y[a,d])) = 0 then f_c[a] = 0 else true endif
);

% 9. Objetivo (incluir penalización por demanda no satisfecha)
var int: total_install_cost_c =
    sum(a in 1..nA, d in 1..nD)( install_cost_c[a,d] * bool2int(y[a,d]) );

var int: total_transport_cost_c =
    sum(a in 1..nA)( trans_cost_c[a] * f_c[a] );

var int: penalty_unmet_demand_c = 
    sum(i in C1 union C2)(unmet_demand_c[i] * 1000);  % Penalización alta

var int: total_cost_c = total_install_cost_c + total_transport_cost_c + penalty_unmet_demand_c;

% Configurar búsqueda y optimización
solve :: seq_search([
           int_search([y[a,d] | a in 1..nA, d in 1..nD], input_order, indomain_min),
           int_search(f_c, first_fail, indomain_min)
         ])
      minimize total_cost_c;

% 10. Salida con información detallada y generación de archivos
output [
  "=== RESULTADOS OPTIMIZACIÓN RED DE TUBERÍAS - GRUPO 5 (CP-SAT) ===\n",
  "Grupo: ", show(grupo), "\n",
  "Fecha/Hora: 2025-06-22\n",
  "Estado: Optimizado\n\n",
  
  "--- COSTOS ---\n",
  "Costo Instalación: $", show(fix(total_install_cost_c) div SCALE), ".",
                         show_padding(fix(total_install_cost_c) mod SCALE, 2), "\n",
  "Costo Transporte:  $", show(fix(total_transport_cost_c) div SCALE), ".",
                         show_padding(fix(total_transport_cost_c) mod SCALE, 2), "\n",
  "Penalización:      $", show(fix(penalty_unmet_demand_c) div SCALE), ".",
                         show_padding(fix(penalty_unmet_demand_c) mod SCALE, 2), "\n",
  "COSTO TOTAL:       $", show(fix(total_cost_c) div SCALE), ".",
                         show_padding(fix(total_cost_c) mod SCALE, 2), "\n\n",
  
  "--- ESTADÍSTICAS DE RED ---\n",
  "Nodos: P=", show(nP), " T=", show(nT), " C1=", show(nC1), " C2=", show(nC2), " (Total: ", show(N), ")\n",
  "Arcos totales: ", show(nA), "\n",
  "Arcos activos: ", show(sum(a in 1..nA where fix(f_c[a]) > 0)(1)), "\n",
  "Utilización: ", show(100 * sum(a in 1..nA where fix(f_c[a]) > 0)(1) div nA), "%\n\n",
  
  "--- FLUJOS ---\n",
  "Suministro total: ", show(sum(i in P)(supply[i])), " l/min\n",
  "Demanda total: ", show(sum(i in C1 union C2)(demand[i])), " l/min\n",
  "Flujo enviado: ", show(sum(i in P, a in 1..nA where arc_from[a]=i)(fix(f_c[a])) / SCALE), " l/min\n",
  "Demanda satisfecha: ", show((sum(i in C1 union C2)(demand[i]) - sum(i in C1 union C2)(fix(unmet_demand_c[i])) / SCALE)), " l/min\n",
  "Demanda no satisfecha: ", show(sum(i in C1 union C2)(fix(unmet_demand_c[i])) / SCALE), " l/min\n",
  "Eficiencia: ", show(100 * (1 - sum(i in C1 union C2)(fix(unmet_demand_c[i])) / SCALE / sum(i in C1 union C2)(demand[i]))), "%\n\n",
  
  "--- DIÁMETROS UTILIZADOS ---\n"
] ++
[ if d = 1 then "D" ++ show(diam_mm[d]) ++ "mm: " ++ 
               show(sum(a in 1..nA)(bool2int(fix(y[a,d])))) ++ " arcos\n"
  else "D" ++ show(diam_mm[d]) ++ "mm: " ++ 
       show(sum(a in 1..nA)(bool2int(fix(y[a,d])))) ++ " arcos\n"
  endif | d in 1..nD
] ++
[
  "\n--- DETALLE DE ARCOS ACTIVOS ---\n"
] ++
[ if fix(f_c[a]) > 0 then
    "Arco " ++ show(a) ++ ": " ++ show(arc_from[a]) ++ " -> " ++ show(arc_to[a]) ++ 
    " | Flujo: " ++ show(fix(f_c[a]) / SCALE) ++ " l/min" ++
    " | Diámetro: " ++ 
    if sum(d in 1..nD where fix(y[a,d]))(diam_mm[d]) > 0 then 
      show(sum(d in 1..nD where fix(y[a,d]))(diam_mm[d])) ++ "mm" 
    else "N/A" endif ++ "\n"
  else ""
  endif | a in 1..nA
] ++
[
  "\n=== ARCHIVO GENERADO ===\n",
  "Resultado de optimización completado\n"
];

% Función auxiliar para mostrar padding de números
function string: show_padding(int: num, int: width) =
  if num < 10 /\ width >= 2 then "0" ++ show(num)
  elseif num < 100 /\ width >= 3 then "0" ++ show_padding(num, width-1)
  else show(num)
  endif;