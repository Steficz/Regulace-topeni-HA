// Montazni desticka do centralni krabice — drzi 2x 8CH relay board
// + 24V PSU + 5V PSU; roztece si PREZMUR dle svych desticek ( default:
// 8CH modul 87x56x17 mm, otvory 3.2 mm v rozich 80x50 ).
// PLA staci (desticka se nefreje), 25% infill, 3 steny.
board_l = 80; board_w = 50; hole_d = 3.5; standoff_h = 8;
plate_l = 190; plate_w = 100;
difference() {
  cube([plate_l, plate_w, 4]);
  // 2x sada 4 sroubu pro relay moduly (soba v X za sebou)
  for (bx = [0, 90]) for (p = [[0,0],[board_l,0],[0,board_w],[board_l,board_w]])
    translate([20 + bx + p[0], 20 + p[1], -0.5])
      cylinder(h = 5, d = hole_d);
  // montazni rohy desticky do krabice
  for (p = [[5,5],[plate_l-5,5],[5,plate_w-5],[plate_l-5,plate_w-5]])
    translate([p[0], p[1], -0.5]) cylinder(h = 5, d = 3.2);
}
// postaveni (stojany pod moduly) — tisk zvlast nebo support-free sloupky:
for (bx = [0, 90]) for (p = [[0,0],[board_l,0],[0,board_w],[board_l,board_w]])
  translate([20 + bx + p[0], 20 + p[1], 4])
    difference() { cylinder(h = standoff_h, d = 7);
      translate([0,0,standoff_h-3]) cylinder(h=4, d=hole_d); }
