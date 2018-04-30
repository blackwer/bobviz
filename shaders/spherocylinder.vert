#version 120

attribute vec4 p3d_Vertex;

uniform mat3 p3d_NormalMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;

uniform struct {
  vec4 ambient;
} p3d_LightModel;

uniform struct {
  vec4 ambient;
  vec4 diffuse;
} p3d_Material;

uniform struct p3d_LightSourceParameters {
  // Light color broken up into components, for compatibility with legacy shaders.
  vec4 ambient;
  vec4 diffuse;

  // View-space position.  If w=0, this is a directional light, with
  // the xyz being -direction.
  vec4 position;
} p3d_LightSource[1];

uniform float L;
uniform float diameter;

varying vec4 diffuse,ambientGlobal,ambient;
varying vec3 normal,lightDir;
varying float dist;

void main()
{
    normal = normalize(p3d_NormalMatrix * p3d_Vertex.xyz);

    /* Separate two halves of sphere to get a spherocylinder and then write vertex position */
    vec4 stretched_pos;
    if (p3d_Vertex.z >= 0.0)
        stretched_pos = diameter*p3d_Vertex + vec4(0.0,0.0,0.5*L,0.0);
    else
        stretched_pos = diameter*p3d_Vertex - vec4(0.0,0.0,0.5*L,0.0);
    stretched_pos.w = p3d_Vertex.w;
    gl_Position = p3d_ModelViewProjectionMatrix * (stretched_pos);

    
    /* Compute light distance and light direction */
    vec4 ecPos = p3d_ModelViewMatrix * (stretched_pos);
    vec3 aux = vec3(p3d_LightSource[0].position-ecPos);
    lightDir = normalize(aux);
    dist = length(aux);

    /* Compute the diffuse, ambient and globalAmbient terms */
    diffuse = p3d_Material.diffuse * p3d_LightSource[0].diffuse;

    /* The ambient terms have been separated into a global and local term since one of them */
    /* suffers attenuation */
    ambient = p3d_Material.ambient * p3d_LightSource[0].ambient;
    ambientGlobal = p3d_LightModel.ambient * p3d_Material.ambient;
}
