// ============================================================
// Stenovy box — ESP32-C6 supermini + SHT40 + SCD40 + buck
// Tisk: PLA nebo PETG, 3 steny, 20% infill, bez supportu.
// OpenSCAD: F6 (Render) -> File > Export STL.
// POZOR: pred montazi over rozmery sve desky a posun otvoru.
// ============================================================

/* [Core] */
L = 54;             // delka X (mm)
W = 44;             // hloubka Y
H = 30;             // vyska Z
wall = 2.4;         // tlousta steny
lid_t = 2.5;        // tloustka veka
screw_d = 2.8;      // predvrt pod M3 samorez (PLA 2.8, PETG 2.6)
clearance = 0.3;

/* [Vents] */
vent_slot = 8;      // delka vetraci sterbiny
vent_w = 2.2;       // sirka sterbiny

module body() {
  difference() {
    cube([L, W, H]);
    // dutina od dna po horni okraj (veko samostatne)
    translate([wall, wall, wall])
      cube([L - 2*wall, W - 2*wall, H - wall + clearance]);
    // kabelove pruchodky vzadu dole (dvoulinka ke stenovemu boxu)
    translate([L*0.32, W - wall/2, wall*2.2]) rotate([90,0,0])
      cylinder(h = wall*2 + 0.4, d = 3.4, center = true);
    translate([L*0.68, W - wall/2, wall*2.2]) rotate([90,0,0])
      cylinder(h = wall*2 + 0.4, d = 3.4, center = true);
    // montazni otvory na zed (vyrez do zadni steny, 2x)
    translate([L*0.18, W - wall/2, H*0.62]) cube([11, wall + 0.4, 4], center = true);
    translate([L*0.82, W - wall/2, H*0.62]) cube([11, wall + 0.4, 4], center = true);
    // vetraci sterbiny: predni + zadni stena, spodni pas
    for (r = [0:2]) {
      ty = 5 + r * (vent_slot + 3);
      if (ty + vent_slot < H - 6) {
        translate([-0.5, ty, wall/2 - vent_w/2]) cube([wall + 1, vent_slot, vent_w]);
        translate([-0.5, H - 6 - ty - vent_slot, H - wall/2 - vent_w/2])
          cube([wall + 1, vent_slot, vent_w]);
      }
    }
  }
}

// rohy se zapustenym predvrtem pro sroubky veka
module posts() {
  for (x = [wall + 3.8, L - wall - 3.8], y = [wall + 3.8, W - wall - 3.8]) {
    difference() {
      translate([x - 3, y - 3, wall]) cube([6, 6, H - wall - 0.01]);
      translate([x, y, wall - 0.5]) cylinder(h = H - wall + 1, d = screw_d);
    }
  }
}

module lid() {
  difference() {
    cube([L, W, lid_t]);
    for (x = [wall + 3.8, L - wall - 3.8], y = [wall + 3.8, W - wall - 3.8])
      translate([x, y, -0.5]) cylinder(h = lid_t + 1, d = screw_d + 0.6);
    // odvetravani navrch (CO2/c6 teple stoupá — mirna mriezka)
    for (r = [0:1])
      translate([L*0.3 + r*L*0.4, 6, -0.01])
        cube([vent_slot, W - 12, lid_t + 0.2], center = false);
  }
}

/* [Render] */
mode = 0; // 0 = body (tisk doly na stul), 1 = viko, 2 = nahled vse

if (mode == 0) body();
else if (mode == 1) translate([0, 0, 0]) lid();
else { body(); translate([L + 8, 0, 0]) lid(); }
