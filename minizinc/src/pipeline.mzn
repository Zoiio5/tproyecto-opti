% Modelo MiniZinc para el Grupo 5
% Con diámetros D2=75 mm, D3=100 mm, D5=150 mm
% y costos de instalación tipo a y b

% ============================
% 1. Parámetros de tamaño y nodos
% ============================
int: nP;                        % Número de plantas
int: nT;                        % Número de tanques
int: nC1;                       % Número de nodos C1 (transbordo)
int: nC2;                       % Número de nodos C2 (finales)
int: N = nP + nT + nC1 + nC2;   % Total de nodos

set of int: P  = 1..nP;                          % Plantas
set of int: T  = nP+1 .. nP+nT;                  % Tanques
set of int: C1 = nP+nT+1 .. nP+nT+nC1;          % Nodos transbordo
set of int: C2 = nP+nT+nC1+1 .. N;              % Nodos finales

% ============================
% 2. Arcos (A)
% ============================
int: nA;                                  % Número total de arcos
array[1..nA] of int: arc_from;            % Nodo origen de cada arco
array[1..nA] of int: arc_to;              % Nodo destino de cada arco

% ============================
% 3. Demandas
% ============================
% Demanda en cada nodo (l/min)
% Para plantas: demanda = 0 (solo suministran)
% Para tanques: demanda = 0 (solo redistribuyen)
% Para C1 y C2: demanda ~ U(40,100) según especificación
array[1..N] of int: demand;

% ============================
% 4. Diámetros disponibles para Grupo 5
% ============================
int: nD = 3;                             % 3 diámetros disponibles
array[1..nD] of int: diam_val = [75, 100, 150];  % D2, D3, D5 en mm
array[1..nD] of int: capacity = [795, 1414, 3181]; % Capacidades máximas en l/min

% ============================
% 5. Costos
% ============================
% Costo de instalación para cada arco y diámetro
% Grupo 5 usa costos tipo a y b:
% Tipo a: [20, 24, 32] para D2, D3, D5
% Tipo b: [50, 62, 78] para D2, D3, D5
array[1..nA, 1..nD] of int: install_cost;

% Costo de transporte por unidad de flujo en cada arco
% Según especificación: c_ij ~ N(8, 2)
array[1..nA] of float: trans_cost;

% ============================
% 6. Variables de decisión
% ============================
% y[a,d] = 1 si se instala diámetro d en arco a; 0 en caso contrario
array[1..nA, 1..nD] of var bool: y;

% f[a] = flujo (en l/min) por el arco a
array[1..nA] of var float: f;

% ============================
% 7. Restricciones
% ============================

% 7.1 A lo más un diámetro por arco (puede no instalarse tubería)
constraint
  forall(a in 1..nA) (
    sum(d in 1..nD)(bool2int(y[a,d])) <= 1
  );

% 7.2 Flujo no excede capacidad del diámetro instalado
constraint
  forall(a in 1..nA) (
    f[a] <= sum(d in 1..nD)(capacity[d] * bool2int(y[a,d]))
  );

% 7.3 Conservación de flujo en tanques (T)
% Flujo entrante = Flujo saliente (sin demanda propia)
constraint
  forall(i in T) (
    sum(a in 1..nA where arc_to[a] = i)(f[a]) = 
    sum(a in 1..nA where arc_from[a] = i)(f[a])
  );

% 7.4 Balance en nodos de transbordo (C1)
% Flujo entrante = demanda propia + flujo saliente
constraint
  forall(i in C1) (
    sum(a in 1..nA where arc_to[a] = i)(f[a]) = 
    demand[i] + sum(a in 1..nA where arc_from[a] = i)(f[a])
  );

% 7.5 Balance en nodos finales (C2)
% Flujo entrante = demanda exacta (no redistribuyen)
constraint
  forall(i in C2) (
    sum(a in 1..nA where arc_to[a] = i)(f[a]) = demand[i]
  );

% 7.6 Flujo no negativo
constraint
  forall(a in 1..nA)(f[a] >= 0.0);

% 7.7 Restricción adicional: Las plantas deben generar suficiente flujo
% El flujo total saliente de plantas debe >= demanda total del sistema
constraint
  sum(i in P, a in 1..nA where arc_from[a] = i)(f[a]) >= 
  sum(i in C1 union C2)(demand[i]);

% ============================
% 8. Función objetivo
% ============================
% Minimizar: Costo total = Costo instalación + Costo transporte

var float: total_install_cost = 
  sum(a in 1..nA, d in 1..nD)(install_cost[a,d] * bool2int(y[a,d]));

var float: total_transport_cost = 
  sum(a in 1..nA)(trans_cost[a] * f[a]);

var float: total_cost = total_install_cost + total_transport_cost;

solve minimize total_cost;

% ============================
% 9. Salida de resultados
% ============================
output [
  "=== RESULTADOS GRUPO 5 ===\n",
  "Diámetros usados: D2(75mm), D3(100mm), D5(150mm)\n",
  "Costos de instalación: tipos a y b\n\n",
  
  "COSTOS:\n",
  "- Instalación total: ", show_float(0, 2, total_install_cost), "\n",
  "- Transporte total:  ", show_float(0, 2, total_transport_cost), "\n",
  "- COSTO TOTAL:       ", show_float(0, 2, total_cost), "\n\n",
  
  "INSTALACIONES (y[arco,diámetro]):\n"
] ++
[
  if sum(d in 1..nD)(bool2int(y[a,d])) > 0 then
    "Arco " ++ show(a) ++ " (" ++ show(arc_from[a]) ++ "->" ++ show(arc_to[a]) ++ "): " ++
    if y[a,1] then "D2(75mm)" 
    else if y[a,2] then "D3(100mm)"
    else if y[a,3] then "D5(150mm)"
    else "ERROR" endif endif endif ++ 
    ", flujo=" ++ show_float(0, 1, f[a]) ++ "\n"
  else ""
  endif
  | a in 1..nA
] ++
[
  "\nFLUJOS POR ARCO:\n"
] ++
[
  if f[a] > 0.001 then
    "f[" ++ show(a) ++ "] = " ++ show_float(0, 2, f[a]) ++ " l/min\n"
  else ""
  endif
  | a in 1..nA
];