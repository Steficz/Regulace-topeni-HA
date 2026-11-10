// Prechodova krabicka u radiatoru: prichod silne dvourilky + konektor pohonu
// PETG (tezsi teplotni okoli radiátoru). Tisk: doly na stul, 3 steny, 20%.
L = 45; W = 30; H = 22; wall = 2.4; clearance = 0.3;
difference() {
  cube([L, W, H]);
  translate([wall, wall, wall])
    cube([L-2*wall, W-2*wall, H-wall+clearance]);
  // kabelovy pruchod (silna linka) — 1 oval 5x3.2
  translate([L/2, W-wall/2, H/2]) rotate([90,0,0])
    scale([1.6,1,1]) cylinder(h=wall*2+0.4, d=3.2, center=true);
  // prechod na konektor pohonu — 2x 3.2 vpredu
  translate([L*0.35, wall/2, H*0.45]) rotate([90,0,0])
    cylinder(h=wall+0.4, d=3.2, center=true);
  translate([L*0.65, wall/2, H*0.45]) rotate([90,0,0])
    cylinder(h=wall+0.4, d=3.2, center=true);
}
