import qupath.lib.io.GsonTools
import qupath.lib.images.servers.LabeledImageServer

def project = getProject()
for (entry in project.getImageList()) {
    def imageData = entry.readImageData()
    def hierarchy = imageData.getHierarchy()
    def annotations = hierarchy.getAnnotationObjects()
    def name = entry.getImageName()

    def OUTPUT_DIR = '/home/yucheng/yucheng/2024/resesarch/KPIS/KPIS_data_raw/DN' 
    //def name = GeneralTools.getNameWithoutExtension(imageData.getServer().getMetadata().getName())
//    def filePath = buildFilePath(OUTPUT_DIR, name.toString())
    def filePath = OUTPUT_DIR + entry.getImageName()

    mkdirs(filePath)
    boolean prettyPrint = true
    def gson = GsonTools.getInstance(prettyPrint)

    def writer = new FileWriter(filePath+'.json');
    gson.toJson(annotations,writer)
    writer.flush()
    print("done")
}