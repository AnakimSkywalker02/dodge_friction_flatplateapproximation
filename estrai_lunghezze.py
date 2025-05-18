import bpy
import bmesh

def calcola_lunghezza_mesh(nome_oggetto):
    obj = bpy.data.objects[nome_oggetto]
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    
    lunghezza_totale = sum(edge.calc_length() for edge in bm.edges)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return lunghezza_totale

# Calcola lunghezze
lunghezza_dorso = calcola_lunghezza_mesh("centerline_dorso")
lunghezza_ventre = calcola_lunghezza_mesh("centerline_ventre")

# Salva su file
filepath_dorso = bpy.path.abspath("//lunghezza_dorso.txt")
filepath_ventre = bpy.path.abspath("//lunghezza_ventre.txt")

with open(filepath_dorso, "w") as f:
    f.write(str(lunghezza_dorso))
with open(filepath_ventre, "w") as f:
    f.write(str(lunghezza_ventre))

print(f"\n✅ Lunghezza dorso: {lunghezza_dorso:.3f} m salvata in: {filepath_dorso}")
print(f"✅ Lunghezza ventre: {lunghezza_ventre:.3f} m salvata in: {filepath_ventre}")