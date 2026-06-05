import os

def combine_project_final():
    # Sadece projenin kök dizinindeki çıktı dosyasını hedefle
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, 'tum_proje_kodlari.txt')
    
    # Kesinlikle uzak durulacak klasör ve dosyalar (Gürültüyü engellemek için)
    ignore_folders = {
        '.git', '.venv', 'venv', 'env', 'build', 'dist', 
        '__pycache__', '.pytest_cache', '.understand-anything', 'node_modules'
    }
    ignore_files = {
        'tum_proje_kodlari.txt', 'kod_birlestir.py', 'kod_birlestir_kesin.py',
        'kod_birlestir_final.py', 'leveltodo.db', 'leveltodo.db-journal', '.DS_Store'
    }
    
    file_count = 0
    
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(current_dir):
            # Üst klasör kontrolleriyle gereksiz dizinleri tamamen buda
            dirs[:] = [d for d in dirs if d not in ignore_folders and not d.startswith('.')]
            
            for file in files:
                if file in ignore_files or file.endswith('.pyc'):
                    continue
                    
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, current_dir)
                
                # Sadece senin mimarinin parçası olan kaynak dosyaları oku
                if file.endswith(('.py', '.toml', '.ini', '.md', '.mako')):
                    try:
                        outfile.write(f"\n--- START OF FILE: {relative_path} ---\n")
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                        outfile.write(f"\n--- END OF FILE: {relative_path} ---\n")
                        file_count += 1
                    except Exception as e:
                        outfile.write(f"[Hata: {relative_path} okunamadı - {str(e)}]\n")
                        
    print(f"✨ Harika! Toplam {file_count} adet temiz kaynak dosyası birleştirildi.")
    print(f"📂 Dosyan tam olarak burada oluşturuldu:\n   {output_path}")

if __name__ == '__main__':
    combine_project_final()