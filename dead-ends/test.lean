-- Test 1 : Afficher la version de Lean
#eval Lean.versionString

-- Test 2 : Un calcul simple
#eval 2 + 2

-- Test 3 : Une preuve triviale
theorem deux_plus_deux : 2 + 2 = 4 := by rfl
